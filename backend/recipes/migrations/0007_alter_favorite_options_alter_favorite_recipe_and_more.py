# Generated by Django 4.1.7 on 2023-03-14 08:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0006_rename_description_recipe_text"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "default_related_name": "favorite",
                "ordering": ("id",),
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
            },
        ),
        migrations.AlterField(
            model_name="favorite",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="recipes.recipe",
                verbose_name="Рецепты",
            ),
        ),
        migrations.AlterField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]