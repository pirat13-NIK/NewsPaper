from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    """Очищает весь кэш приложения."""
    help = 'Очищает весь кэш'

    def handle(self, *args, **options):
        """Выполняет полную очистку кэша."""
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Весь кэш успешно очищен!'))