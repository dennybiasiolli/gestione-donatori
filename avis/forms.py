from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''  # Removes ':' as label suffix

    username = UsernameField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
                'placeholder': 'Nome utente',
            },
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
            },
        ),
    )
