from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from users.validators import validate_username, validate_name


class User(AbstractUser):
    """Модель Пользователя."""

    email = models.EmailField(
        verbose_name='Почта',
        max_length=settings.EMAIL_MAX_LENGHT,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.USERS_MAX_LENGHT,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator, ),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.USERS_MAX_LENGHT,
        blank=False,
        validators=(validate_name, ),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.USERS_MAX_LENGHT,
        blank=False,
        validators=(validate_name, ),
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.USERS_MAX_LENGHT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'
