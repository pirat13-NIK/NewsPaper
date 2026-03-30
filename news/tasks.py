from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import Post, Category
from django.contrib.auth.models import User


@shared_task
def send_notification_to_subscribers_async(post_id):
    """Асинхронная отправка уведомлений подписчикам при создании новости"""
    try:
        post = Post.objects.get(id=post_id)
        categories = post.categories.all()

        if not categories.exists():
            return f"Пост {post_id} не имеет категорий"

        # Собираем уникальных подписчиков
        subscribers = set()
        for category in categories:
            for subscriber in category.subscribers.all():
                subscribers.add(subscriber)

        if not subscribers:
            return f"Нет подписчиков для поста {post_id}"

        # Отправляем письмо каждому подписчику
        sent_count = 0
        for subscriber in subscribers:
            # Создаем HTML-контент письма
            html_content = render_to_string(
                'news/email_notification.html',
                {
                    'post': post,
                    'username': subscriber.username,
                    'preview_text': post.preview_50(),
                    'post_type_display': post.get_post_type_display(),
                    'site_url': 'http://127.0.0.1:8000'
                }
            )

            text_content = strip_tags(html_content)

            # Тема письма
            subject = f'Новая {post.get_post_type_display().lower()} в вашем любимом разделе: {post.title}'

            # Отправляем email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email]
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            sent_count += 1

        return f"Отправлено {sent_count} уведомлений для поста {post_id}"

    except Post.DoesNotExist:
        return f"Пост {post_id} не найден"
    except Exception as e:
        return f"Ошибка при отправке: {str(e)}"


@shared_task
def send_weekly_newsletter():
    try:
        week_ago = timezone.now() - timedelta(days=7)

        categories = Category.objects.all()

        total_sent = 0

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

            for subscriber in subscribers:
                html_content = render_to_string(
                    'news/weekly_newsletter.html',
                    {
                        'username': subscriber.username,
                        'category': category,
                        'posts': new_posts,
                        'week_ago': week_ago,
                        'site_url': 'http://127.0.0.1:8000'
                    }
                )

                text_content = strip_tags(html_content)

                subject = f'Еженедельная рассылка: {new_posts.count()} новых статей в категории "{category.name}"'

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email]
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
                total_sent += 1

        return f"Еженедельная рассылка завершена. Отправлено {total_sent} писем."

    except Exception as e:
        return f"Ошибка при отправке еженедельной рассылки: {str(e)}"


@shared_task
def send_welcome_email_async(user_id):
    try:
        from django.contrib.auth.models import User
        from allauth.account.utils import send_email_confirmation

        user = User.objects.get(id=user_id)

        from allauth.account.adapter import get_adapter
        from allauth.account.models import EmailAddress

        email_address = EmailAddress.objects.get(user=user, primary=True)
        adapter = get_adapter()
        adapter.send_confirmation_mail(None, email_address)

        return f"Приветственное письмо отправлено пользователю {user.email}"

    except Exception as e:
        return f"Ошибка при отправке приветственного письма: {str(e)}"