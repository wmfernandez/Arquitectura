from django.contrib.auth.forms import AuthenticationForm
from django import forms

class DNIAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="DNI / CI",
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
