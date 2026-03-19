from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # Добавьте этот импорт


def home_redirect(request):
    return redirect('news_list')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', home_redirect, name='home'),
    path('', include('news.urls')),
]
