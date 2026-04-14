from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import Author
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter


@login_required
def profile(request):
    """Страница профиля пользователя."""
    return render(request, 'account/profile.html')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля: имя, фамилия, email."""
    model = User
    template_name = 'account/profile_edit.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя."""
        return self.request.user


@login_required
def become_author(request):
    """Назначает пользователю права автора (группа 'authors')."""
    authors_group, created = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors_group)
    messages.success(request, 'Права автора подтверждены. Начните публикацию.')
    return redirect('news_list')


@login_required
def resend_confirmation(request):
    """Повторно отправляет письмо для подтверждения email."""
    try:
        email_address = EmailAddress.objects.get(user=request.user, verified=False)
        adapter = get_adapter(request)
        adapter.send_confirmation_mail(request, email_address)

        messages.success(request, 'Письмо с подтверждением отправлено повторно! Проверьте вашу почту.')
    except EmailAddress.DoesNotExist:
        messages.error(request, 'Не удалось отправить письмо. Возможно, ваш email уже подтвержден.')

    return redirect('account_email')