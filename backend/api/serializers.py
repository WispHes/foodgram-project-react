from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import User
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscription, Tag)


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password',
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context["request"].user.is_authenticated:
            return Subscription.objects.filter(
                user=self.context["request"].user, author=obj.pk
            ).exists()
        return False


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для работы с подписками."""

    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ("recipes", "recipes_count")
        )

    def get_queryset(self, obj):
        return Recipe.objects.filter(author=obj.pk)

    def get_recipes(self, obj):
        serializer = RecipeSerializer(
            self.get_queryset(obj),
            many=True,
            context={"request": self.context.get("request")},
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return self.get_queryset(obj).count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit', )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    unit = serializers.CharField(source='ingredient.unit', required=False)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_request(self, ):
        return self.context.get('request')

    def get_is_favorited(self, obj):
        user = self.get_request().user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.get_request() and self.get_request().user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=self.get_request().user, recipe=obj
            ).exists()
        return False


class CreateRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания рецепта """
    ingredients = RecipeIngredientSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'}
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)

    def validate(self, data):
        for tag in data['tags']:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    {'tags': 'Указанного тега не существует'}
                )
        if data['cooking_time'] < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время готовки не меньше одной минуты'}
            )
        ingredients = data['ingredients']
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Отсутствуют ингридиенты'}
            )
        for ingredient in ingredients:
            if ingredient['ingredient']['id'] in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингридиенты должны быть уникальны'}
                )
            ingredients_list.append(ingredient['ingredient']['id'])

        return data

    def create_ingredient_amount(self, ingredient_data, recipe):
        return IngredientAmount(
            ingredient_id=ingredient_data['ingredient']['id'],
            amount=ingredient_data['amount'],
            recipe=recipe,
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.set(tags_data)

        ingredient_amounts = [
            self.create_ingredient_amount(ingredient_data, recipe)
            for ingredient_data in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)

        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientAmount.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop('ingredients')

        ingredient_amounts = [
            self.create_ingredient_amount(ingredient_data, instance)
            for ingredient_data in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полей избранного."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор."""

    class Meta:
        abstract = True
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if (
            user.favorite.filter(recipe=recipe).exists() or
            user.shopping_cart.filter(recipe=recipe).exists()
        ):
            raise serializers.ValidationError('Рецепт уже добавлен')
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(BaseSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta(BaseSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseSerializer):
    """Сериализатор для списка покупок"""

    class Meta(BaseSerializer.Meta):
        model = ShoppingCart
