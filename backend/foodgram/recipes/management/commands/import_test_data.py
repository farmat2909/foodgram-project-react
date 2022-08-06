import csv
import subprocess as sub

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда 'import_test_data' проводит миграции и
    загружает тестовые данные в базу из csv файлов.
    """
    def handle(self, *args, **options):
        self.import_ingredient()

        print('Загрузка тестовых данных завершена.')


    def import_ingredient(self, file='ingredients.csv'):
        print(f'Загрузка {file}...')
        file_path = f'data/{file}'
        with open(file_path, newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'measurement_unit']
            reader = csv.DictReader(f, fieldnames=fieldnames)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
