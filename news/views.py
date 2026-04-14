from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Post, Category, Comment
from .filters import NewsFilter
from .utils import check_daily_post_limit, get_remaining_posts_today
from .tasks import send_notification_to_subscribers_async
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


def get_cached_post(post_id, post_type='NW'):
    """Получает пост из кэша или из базы данных."""
    cache_key = f'post_detail_{post_id}_{post_type}'
    post = cache.get(cache_key)

    if post is None:
        try:
            post = Post.objects.get(id=post_id, post_type=post_type)
            cache.set(cache_key, post, 3600)  # Кэшируем на 1 час
        except Post.DoesNotExist:
            return None

    return post


def invalidate_post_cache(post):
    """Очищает кэш для конкретного поста."""
    cache.delete(f'post_detail_{post.id}_{post.post_type}')
    cache.delete('news_list_cache')
    cache.delete('category_list_cache')
    for i in range(1, 10):
        cache.delete(f'news_list_page_{i}')


@cache_page(60)
def news_list(request):
    """Список всех новостей с пагинацией (10 на страницу)."""
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_list.html', {'page_obj': page_obj})


@cache_page(60 * 5)
def news_detail(request, news_id):
    """Детальная страница новости с комментариями."""
    news_item = get_object_or_404(Post, id=news_id, post_type='NW')
    comments = news_item.comment_set.all().order_by('-created_at')
    return render(request, 'news/news_detail.html', {
        'article_item': news_item,
        'comments': comments
    })


def news_search(request):
    """Поиск новостей с фильтрацией и пагинацией."""
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    news_filter = NewsFilter(request.GET, queryset=news)
    paginator = Paginator(news_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_search.html', {
        'filter': news_filter,
        'page_obj': page_obj
    })


@login_required
def subscribe_to_category(request, category_id):
    """Подписывает пользователя на категорию."""
    category = get_object_or_404(Category, id=category_id)

    if request.user in category.subscribers.all():
        messages.warning(request, f'Вы уже подписаны на категорию "{category.name}"')
    else:
        category.subscribers.add(request.user)
        messages.success(request, f'Вы успешно подписались на категорию "{category.name}"')
        cache.delete('category_list_cache')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


@login_required
def unsubscribe_from_category(request, category_id):
    """Отписывает пользователя от категории."""
    category = get_object_or_404(Category, id=category_id)

    if request.user in category.subscribers.all():
        category.subscribers.remove(request.user)
        messages.success(request, f'Вы отписались от категории "{category.name}"')
        cache.delete('category_list_cache')
    else:
        messages.warning(request, f'Вы не были подписаны на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


def send_notification_to_subscribers(post):
    """Отправляет email-уведомления подписчикам категорий поста."""
    from django.contrib.auth.models import User

    categories = post.categories.all()
    recipients = set()

    for category in categories:
        for subscriber in category.subscribers.all():
            recipients.add(subscriber.email)

    if not recipients:
        return

    for email in recipients:
        user = User.objects.get(email=email)

        html_content = render_to_string(
            'news/email_notification.html',
            {
                'post': post,
                'username': user.username,
                'preview_text': post.preview_50(),
                'post_type': post.get_post_type_display()
            }
        )

        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=f"Новая {post.get_post_type_display().lower()}: {post.title}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@method_decorator(cache_page(60 * 10), name='dispatch')
class CategoryListView(LoginRequiredMixin, ListView):
    """Список всех категорий (только для авторизованных)."""
    model = Category
    template_name = 'news/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание новости (только для авторов, с проверкой лимита)."""
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет дневной лимит публикаций."""
        if not check_daily_post_limit(request.user):
            messages.error(request, 'Вы превысили лимит публикаций!')
            return redirect('news_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Сохраняет новость, отправляет уведомления и очищает кэш."""
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = self.request.user.author
        post.save()
        form.save_m2m()

        send_notification_to_subscribers_async.delay(post.id)

        invalidate_post_cache(post)

        remaining = get_remaining_posts_today(self.request.user)
        messages.success(self.request, f'Новость создана! Осталось публикаций: {remaining} из 3')
        return super().form_valid(form)


class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование новости (только свои новости)."""
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'

    def get_queryset(self):
        """Возвращает только новости."""
        return Post.objects.filter(post_type='NW')

    def has_permission(self):
        """Проверяет, что пользователь - автор новости."""
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def form_valid(self, form):
        """Очищает кэш после обновления."""
        response = super().form_valid(form)

        invalidate_post_cache(self.object)

        messages.success(self.request, 'Новость успешно обновлена!')
        return response

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'Вы можете редактировать только свои новости!')
        return redirect('news_list')


class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление новости (только свои новости)."""
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'

    def get_queryset(self):
        """Возвращает только новости."""
        return Post.objects.filter(post_type='NW')

    def has_permission(self):
        """Проверяет, что пользователь - автор новости."""
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def delete(self, request, *args, **kwargs):
        """Очищает кэш перед удалением."""
        post = self.get_object()
        invalidate_post_cache(post)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Новость успешно удалена!')
        return response

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'Вы можете удалять только свои новости!')
        return redirect('news_list')


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание статьи (только для авторов, с проверкой лимита)."""
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def dispatch(self, request, *args, **kwargs):
        """Проверяет дневной лимит публикаций."""
        if not check_daily_post_limit(request.user):
            messages.error(request, 'Вы превысили лимит публикаций!')
            return redirect('news_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Сохраняет статью, отправляет уведомления и очищает кэш."""
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = self.request.user.author
        post.save()
        form.save_m2m()

        send_notification_to_subscribers_async.delay(post.id)
        invalidate_post_cache(post)

        remaining = get_remaining_posts_today(self.request.user)
        messages.success(self.request, f'Статья создана! Осталось публикаций: {remaining} из 3')
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирование статьи (только свои статьи)."""
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'

    def get_queryset(self):
        """Возвращает только статьи."""
        return Post.objects.filter(post_type='AR')

    def has_permission(self):
        """Проверяет, что пользователь - автор статьи."""
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def form_valid(self, form):
        """Очищает кэш после обновления."""
        response = super().form_valid(form)
        invalidate_post_cache(self.object)
        messages.success(self.request, 'Статья успешно обновлена!')
        return response

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'Вы можете редактировать только свои статьи!')
        return redirect('news_list')


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление статьи (только свои статьи)."""
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'

    def get_queryset(self):
        """Возвращает только статьи."""
        return Post.objects.filter(post_type='AR')

    def has_permission(self):
        """Проверяет, что пользователь - автор статьи."""
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def delete(self, request, *args, **kwargs):
        """Очищает кэш перед удалением."""
        post = self.get_object()
        invalidate_post_cache(post)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Статья успешно удалена!')
        return response

    def handle_no_permission(self):
        """Обработка отказа в доступе."""
        messages.error(self.request, 'Вы можете удалять только свои статьи!')
        return redirect('news_list')


@cache_page(60 * 5)
def article_detail(request, article_id):
    """Детальная страница статьи с комментариями."""
    article_item = get_object_or_404(Post, id=article_id, post_type='AR')
    comments = article_item.comment_set.all().order_by('-created_at')
    return render(request, 'news/article_detail.html', {
        'article_item': article_item,
        'comments': comments
    })


@login_required
@require_POST
def add_comment(request, post_id):
    """Добавляет комментарий к новости или статье."""
    post = get_object_or_404(Post, id=post_id)
    text = request.POST.get('text', '').strip()

    if text:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )
        cache.delete(f'post_comments_{post_id}')
        messages.success(request, 'Комментарий добавлен!')
    else:
        messages.error(request, 'Комментарий не может быть пустым!')

    if post.post_type == 'NW':
        return redirect('news_detail', news_id=post_id)
    else:
        return redirect('article_detail', article_id=post_id)