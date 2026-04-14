from django.core.management.base import BaseCommand
from news.tasks import send_weekly_newsletter


class Command(BaseCommand):
    """Команда для тестирования еженедельной рассылки."""
    help = 'Тестирует еженедельную рассылку'

    def handle(self, *args, **options):
        """Запускает асинхронную задачу send_weekly_newsletter."""
        self.stdout.write('Запуск тестовой рассылки...')
        result = send_weekly_newsletter.delay()
        self.stdout.write(self.style.SUCCESS(f'Задача отправлена! ID: {result.id}'))