from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.apps import apps


class Command(BaseCommand):
    help = 'Отправляет еженедельную рассылку новых статей подписчикам'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю отправку еженедельной рассылки...')

        Category = apps.get_model('news', 'Category')
        Post = apps.get_model('news', 'Post')

        week_ago = timezone.now() - timedelta(days=7)
        total_emails = 0
        total_categories = 0

        categories = Category.objects.all()

        for category in categories:
            new_posts = Post.objects.filter(
                categories=category,
                created_at__gte=week_ago
            ).order_by('-created_at')

            if not new_posts.exists():
                continue

            subscribers = category.subscribers.all()

            if not subscribers:
                continue

            total_categories += 1

            for subscriber in subscribers:
                html_content = render_to_string(
                    'news/weekly_newsletter.html',
                    {
                        'username': subscriber.username,
                        'category': category,
                        'posts': new_posts,
                        'week_start': week_ago.date(),
                        'week_end': timezone.now().date(),
                        'posts_count': new_posts.count(),
                        'site_url': settings.SITE_URL
                    }
                )

                text_content = strip_tags(html_content)

                subject = f'Еженедельная рассылка: {new_posts.count()} новых статей в категории "{category.name}"'

                try:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[subscriber.email]
                    )
                    msg.attach_alternative(html_content, 'text/html')
                    msg.send()

                    total_emails += 1
                    self.stdout.write(f'Письмо отправлено {subscriber.email} для категории "{category.name}"')

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при отправке {subscriber.email}: {str(e)}')
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Рассылка успешно завершена! Отправлено писем: {total_emails}'
        ))