from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Post
from .filters import NewsFilter


# Ваши функции (сохранены без изменений)
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

class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'news/news_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = self.request.user.author
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для создания новостей. Необходимо стать автором!')
        return redirect('become_author')


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'news/article_edit.html'
    fields = ['title', 'text', 'categories']
    success_url = reverse_lazy('news_list')
    permission_required = 'news.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = self.request.user.author
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для создания статей. Необходимо стать автором!')
        return redirect('become_author')


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

        # Проверяем, является ли пользователь автором этого поста
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