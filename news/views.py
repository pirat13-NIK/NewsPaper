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
from .models import Post, Category
from .filters import NewsFilter
from .utils import check_daily_post_limit, get_remaining_posts_today
from .tasks import send_notification_to_subscribers_async


# Ваши функции
def news_list(request):
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_list.html', {'page_obj': page_obj})


def news_search(request):
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    news_filter = NewsFilter(request.GET, queryset=news)
    paginator = Paginator(news_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_search.html', {
        'filter': news_filter,
        'page_obj': page_obj
    })


def news_detail(request, news_id):
    news_item = get_object_or_404(Post, id=news_id, post_type='NW')
    return render(request, 'news/news_detail.html', {'news_item': news_item})


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.user in category.subscribers.all():
        messages.warning(request, f'Вы уже подписаны на категорию "{category.name}"')
    else:
        category.subscribers.add(request.user)
        messages.success(request, f'Вы успешно подписались на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


@login_required
def unsubscribe_from_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.user in category.subscribers.all():
        category.subscribers.remove(request.user)
        messages.success(request, f'Вы отписались от категории "{category.name}"')
    else:
        messages.warning(request, f'Вы не были подписаны на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


def send_notification_to_subscribers(post):
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


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def dispatch(self, request, *args, **kwargs):
        if not check_daily_post_limit(request.user):
            remaining = get_remaining_posts_today(request.user)
            messages.error(
                request,
                f'Вы превысили лимит публикаций! Можно создавать не более 3 постов в сутки.\n'
                f'Сегодня вы уже использовали все попытки. Попробуйте завтра.'
            )
            return redirect('news_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = self.request.user.author
        post.save()
        form.save_m2m()

        send_notification_to_subscribers_async.delay(post.id)

        remaining = get_remaining_posts_today(self.request.user)
        messages.success(
            self.request,
            f'Новость успешно создана! Уведомления отправляются подписчикам.\n'
            f'Сегодня осталось публикаций: {remaining} из 3'
        )
        return super().form_valid(form)


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def dispatch(self, request, *args, **kwargs):
        if not check_daily_post_limit(request.user):
            remaining = get_remaining_posts_today(request.user)
            messages.error(
                request,
                f'Вы превысили лимит публикаций! Можно создавать не более 3 постов в сутки.\n'
                f'Сегодня вы уже использовали все попытки. Попробуйте завтра.'
            )
            return redirect('news_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = self.request.user.author
        post.save()
        form.save_m2m()

        send_notification_to_subscribers_async.delay(post.id)

        remaining = get_remaining_posts_today(self.request.user)
        messages.success(
            self.request,
            f'Статья успешно создана! Уведомления отправляются подписчикам.\n'
            f'Сегодня осталось публикаций: {remaining} из 3'
        )
        return super().form_valid(form)


class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')

    def has_permission(self):
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы можете редактировать только свои новости!')
        return redirect('news_list')


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.change_post'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def has_permission(self):
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы можете редактировать только свои статьи!')
        return redirect('news_list')


class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')

    def has_permission(self):
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы можете удалять только свои новости!')
        return redirect('news_list')


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = 'news.delete_post'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def has_permission(self):
        has_perm = super().has_permission()
        if not has_perm:
            return False
        post = self.get_object()
        return self.request.user == post.author.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы можете удалять только свои статьи!')
        return redirect('news_list')


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'news/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']