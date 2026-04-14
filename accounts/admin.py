from django.contrib import admin
from .models import Author
from news.models import Category, Post, Comment


def nullify_rating(modeladmin, request, queryset):
    """Обнуляет рейтинг выбранных объектов."""
    queryset.update(rating=0)
nullify_rating.short_description = 'Обнулить рейтинг'


class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий."""
    list_display = ('name',)
    search_fields = ('name',)

class PostAdmin(admin.ModelAdmin):
    """Админ-панель для постов с фильтрацией и поиском."""
    list_display = ('title', 'post_type', 'rating', 'created_at')
    list_filter = ('post_type', 'rating', 'created_at')
    search_fields = ('title', 'text', 'author__user__username')
    actions = [nullify_rating]


class CommentAdmin(admin.ModelAdmin):
    """Админ-панель для комментариев с сокращённым текстом."""
    list_display = ('text_short', 'user', 'post', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'user__username', 'post__title')
    actions = [nullify_rating]

    def text_short(self, obj):
        """Возвращает первые 50 символов комментария."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст'


class AuthorAdmin(admin.ModelAdmin):
    """Админ-панель для авторов."""
    list_display = ('user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username',)
    actions = [nullify_rating]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Author, AuthorAdmin)