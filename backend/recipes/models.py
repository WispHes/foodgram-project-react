from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models.constraints import UniqueConstraint

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=255,
    )
    unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=64,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.unit}'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        verbose_name='Название тега',
        max_length=255,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True,
        validators=[
                RegexValidator(
                    r'^#[A-Fa-f0-9]{6}$', message='Введите цвет в формате HEX'
                )
            ],
        )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=255,
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(720)],
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('pub_date', )
        verbose_name = 'Рецептов'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author.email}, {self.name}'

    def clean(self):
        if self.cooking_time <= 0:
            raise ValidationError(
                'Время приготовления должно быть положительным числом.'
            )

    def favorite_count(self):
        return self.favorite.count()


class IngredientAmount(models.Model):
    """Модель для кол-ва ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='recipe',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Кол-во ингредиента в рецепте'
        verbose_name_plural = 'Кол-во ингредиентов в рецепте'

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
    )

    def add_recipe(self, recipe):
        self.recipes.add(recipe)

    def remove_recipe(self, recipe):
        self.recipes.remove(recipe)

    class Meta:
        ordering = ('id', )
        default_related_name = 'favorite'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_recipe',
            ),
        ]


class ShoppingCart(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
    )

    class Meta:
        ordering = ('id', )
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_item'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на себя')
        super().save(*args, **kwargs)
