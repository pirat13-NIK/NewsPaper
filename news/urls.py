from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.news_list, name='news_list'),
    path('news/search/', views.news_search, name='news_search'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),

    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
]