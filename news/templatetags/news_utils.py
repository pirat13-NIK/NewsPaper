from django import template
from datetime import date
from django.apps import apps

register = template.Library()


@register.filter(name='get_remaining_posts')
def get_remaining_posts(user):
    if not user.is_authenticated:
        return 0

    Post = apps.get_model('news', 'Post')

    today = date.today()
    posts_today = Post.objects.filter(
        author__user=user,
        created_at__date=today
    ).count()

    return 3 - posts_today