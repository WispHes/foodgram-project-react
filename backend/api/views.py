from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.generate_pdf import generate_shopping_cart_pdf
from api.permissions import AuthorPermission
from api.serializers import (CreateRecipeSerializer, FavoriteSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             TagSerializer, UsersSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscription, Tag)
from users.models import User


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class UsersViewSet(UserViewSet):
    """Вьюсет для работы с пользователями и подписками. """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ["get", "post", "delete", "head"]

    def get_user_and_author(self, request, id):
        return request.user, get_object_or_404(User, id=id)

    @action(
        methods=["POST", ],
        detail=True,
    )
    def subscribe(self, request, id):
        user, author = self.get_user_and_author(request, id)
        if user == author:
            return Response(
                {"error": "Невозможно подписаться на себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription, created = Subscription.objects.get_or_create(
            user=user, author=author
        )
        if created:
            return Response(
                FollowSerializer(
                    author, context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": "Вы уже подписаны"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, id):
        get_object_or_404(
            Subscription, user=request.user,
            author=get_object_or_404(User, pk=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        serializer = FollowSerializer(
            self.paginate_queryset(
                User.objects.filter(following__user=request.user)
            ),
            many=True,
            context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (AuthorPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return CreateRecipeSerializer

    def send_message(self, ingredients, filename):
        shopping_list = "Купить в магазине:"
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__unit']}) - "
                f"{ingredient['amount']}"
            )
        file = filename
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{file}.txt"'
        return response

    def add_to_model(self, serializer_class, model_class, request, pk):
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {"user": request.user.id, "recipe": recipe.id}
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_model(self, model_class, user, recipe_id):
        get_object_or_404(
            model_class,
            user=user,
            recipe=get_object_or_404(Recipe, id=recipe_id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"])
    def download_shopping_cart(self, request):
        return generate_shopping_cart_pdf(request.user)

    @action(
        detail=True,
        methods=("POST", ),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.add_to_model(
            serializer_class=ShoppingCartSerializer,
            model_class=ShoppingCart,
            request=request,
            pk=pk
        )

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        return self.remove_from_model(
            model_class=ShoppingCart,
            user=request.user.id,
            recipe_id=pk
        )

    @action(
        detail=True, methods=("POST", ),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.add_to_model(
            serializer_class=FavoriteSerializer,
            model_class=Favorite,
            request=request,
            pk=pk
        )

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        return self.remove_from_model(
            model_class=Favorite,
            user=request.user.id,
            recipe_id=pk
        )
