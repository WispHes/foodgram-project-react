import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv', 'r', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, unit = row
                try:
                    Ingredient.objects.create(name=name, unit=unit)
                except IntegrityError:
                    self.stdout.write(
                        f'Ингредиент {name} уже существует в базе данных'
                    )
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
