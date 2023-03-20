from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Subscription, Tag)


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

    list_display = ('id', 'name', 'author', 'get_favorites_count', )
    list_filter = ('name', 'author', 'tags', )
    search_fields = ('name', )
    inlines = (IngredientAmountInline,)
    empty_value_display = '-пусто-'

    def get_favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    get_favorites_count.short_description = 'Добавлен в избранное'


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
