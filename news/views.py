from django.shortcuts import render, get_object_or_404
from .models import Post

def news_list(request):
    news = Post.objects.filter(post_type='NW').order_by('-created_at')
    return render(request, 'news/news_list.html', {'news': news})

def news_detail(request, news_id):
    news_item = get_object_or_404(Post, id=news_id, post_type='NW')
    return render(request, 'news/news_detail.html', {'news_item': news_item})
