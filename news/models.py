from django.db import models
from django.contrib.auth.models import User
from accounts.models import Author


class Category(models.Model):
    """Категория поста с возможностью подписки пользователей."""
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscriptions', blank=True)

    def __str__(self):
        """Возвращает название категории."""
        return self.name


class Post(models.Model):
    """Модель поста (новость или статья) с рейтингом и категориями."""
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        """Увеличивает рейтинг поста на 1."""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг поста на 1."""
        self.rating -= 1
        self.save()

    def preview(self):
        """Возвращает первые 124 символа текста."""
        if len(self.text) <= 124:
            return self.text
        return self.text[:124] + '...'

    def preview_50(self):
        """Возвращает первые 50 символов текста."""
        if len(self.text) <= 50:
            return self.text
        return self.text[:50] + '...'

    def __str__(self):
        """Возвращает строковое представление: тип, заголовок и рейтинг."""
        return f"{self.get_post_type_display()}: {self.title} (рейтинг: {self.rating})"


class PostCategory(models.Model):
    """Связующая модель между Post и Category (many-to-many)."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        """Возвращает строку: заголовок поста - название категории."""
        return f"{self.post.title} - {self.category.name}"


class Comment(models.Model):
    """Комментарий пользователя к посту с рейтингом."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        """Увеличивает рейтинг комментария на 1."""
        self.rating += 1
        self.save()

    def dislike(self):
        """Уменьшает рейтинг комментария на 1."""
        self.rating -= 1
        self.save()

    def __str__(self):
        """Возвращает строку: комментарий от пользователя к посту."""
        return f"Комментарий от {self.user.username} к {self.post.title}"