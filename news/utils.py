from datetime import datetime, date
from .models import Post


def check_daily_post_limit(user):
    today = date.today()
    posts_today = Post.objects.filter(
        author__user=user,
        created_at__date=today
    ).count()
    return posts_today < 3

def get_remaining_posts_today(user):
    today = date.today()
    posts_today = Post.objects.filter(
        author__user=user,
        created_at__date=today
    ).count()
    return 3 - posts_today