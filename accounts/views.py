from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import Author


@login_required
def profile(request):
    return render(request, 'account/profile.html')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'account/profile_edit.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def become_author(request):
    """Добавляет пользователя в группу authors"""
    authors_group, created = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors_group)
    messages.success(request, 'Права автора подтверждены. Начните публикацию.')
    return redirect('news_list')