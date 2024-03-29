# Generated by Django 3.2.16 on 2023-03-20 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецептов', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(max_length=1500, verbose_name='Текстовое описание рецепта'),
        ),
    ]
