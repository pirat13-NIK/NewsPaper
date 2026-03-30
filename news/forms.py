from django import forms
from .models import Category

class SubscriptionForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.HiddenInput()
    )