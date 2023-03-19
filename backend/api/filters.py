from django_filters.rest_framework import CharFilter, FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', )

    def _filter_related(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            recipe = name.values_list('recipe', flat=True)
            return queryset.filter(id__in=recipe)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_related(
            queryset,
            self.request.user.favorite,
            value,
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_related(
            queryset,
            self.request.user.shopping_cart,
            value,
        )
