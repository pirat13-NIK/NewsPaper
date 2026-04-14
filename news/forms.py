from django import forms
from .models import Category

class SubscriptionForm(forms.Form):
    """Форма для подписки/отписки от категории (скрытое поле)."""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.HiddenInput()
    )