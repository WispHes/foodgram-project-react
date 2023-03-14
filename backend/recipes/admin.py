from django.contrib import admin, messages
from recipes.models import Ingredient, Tag
from users.models import User

from .models import (Recipe, Ingredient, IngredientAmount,
                     Tag, Favorite, ShoppingCart, Subscription)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    min_num = 1
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name', 'color',)
    search_fields = ('name', 'color',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit')
    list_filter = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    def favorite_count(self, obj):
        return obj.favorite_count()

    favorite_count.short_description = 'Добавлен в избранное'

    list_display = ('id', 'name', 'author', 'favorite_count',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', )
    inlines = (IngredientAmountInline,)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', )
    search_fields = ('user', 'recipe', )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', )
    search_fields = ('user', 'recipe', )
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author',)
    search_fields = (
        'user__email', 'author__email',)
    empty_value_display = '-пусто-'
