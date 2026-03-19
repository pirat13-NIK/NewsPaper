from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import Author

@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    """Автоматически добавляем пользователя в группу common при регистрации"""
    if created:
        common_group, created = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)

@receiver(post_save, sender=User)
def create_author(sender, instance, created, **kwargs):
    """Создаем автора при создании пользователя"""
    if created:
        Author.objects.create(user=instance)