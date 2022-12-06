from django import forms
from django.contrib.auth import get_user_model


class CustomUserSettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["page"]
