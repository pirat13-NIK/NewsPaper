import django_filters
from django import forms
from .models import Post
from django.contrib.auth.models import User


class NewsFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название содержит'
    )

    author__user__username = django_filters.CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Имя автора содержит'
    )

    created_at = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Позже даты',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['title', 'author__user__username', 'created_at']