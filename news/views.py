from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post
from .filters import NewsFilter


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