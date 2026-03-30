from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('become-author/', views.become_author, name='become_author'),
    path('resend-confirmation/', views.resend_confirmation, name='resend_confirmation'),
]
