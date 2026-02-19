from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField

from .models import Donazione


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes ':' as label suffix

    username = UsernameField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "placeholder": "Nome utente",
            },
        )
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            },
        ),
    )


class DonazioneForm(forms.ModelForm):
    class Meta:
        model = Donazione
        fields = ["data_donazione", "tipo_donazione"]
        widgets = {
            "tipo_donazione": forms.Select(
                choices=Donazione.TipoDonazione.choices,
                attrs={
                    "class": "form-select-sm",
                },
            ),
            "data_donazione": forms.DateInput(
                format=("%Y-%m-%d"),
                attrs={
                    "type": "date",
                    "class": "form-control-sm",
                },
            ),
        }
