from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited_and_in_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', )

    def filter_is_favorited_and_in_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(favorites__user=self.request.user) |
                Q(shopping_list__user=self.request.user)
            ).distinct()
        return queryset
