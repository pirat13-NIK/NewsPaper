from datetime import datetime, date
from .models import Post


def check_daily_post_limit(user):
    """Проверяет, не превысил ли пользователь лимит в 3 поста в день."""
    today = date.today()
    posts_today = Post.objects.filter(
        author__user=user,
        created_at__date=today
    ).count()
    return posts_today < 3

def get_remaining_posts_today(user):
    """Возвращает количество оставшихся публикаций на сегодня (макс. 3)."""
    today = date.today()
    posts_today = Post.objects.filter(
        author__user=user,
        created_at__date=today
    ).count()
    return 3 - posts_today