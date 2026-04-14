from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.news_list, name='news_list'),
    path('news/search/', views.news_search, name='news_search'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),

    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),

    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),

    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    path('category/<int:category_id>/subscribe/', views.subscribe_to_category, name='subscribe_category'),
    path('category/<int:category_id>/unsubscribe/', views.unsubscribe_from_category, name='unsubscribe_category'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),

    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]