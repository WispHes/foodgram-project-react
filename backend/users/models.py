from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель Пользователя."""

    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        validators=(
            RegexValidator(
                r'^[a-zA-Zа-яА-ЯёЁ]*$',
                message='Имя может содержать только буквы'
            ),
        )
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        validators=(
            RegexValidator(
                r'^[a-zA-Zа-яА-ЯёЁ]*$',
                message='Имя может содержать только буквы'
            ),
        )
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'
