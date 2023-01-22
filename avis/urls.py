from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import forms, views

urlpatterns = [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            authentication_form=forms.BootstrapAuthenticationForm,
        ),
        name="login",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.index, name="index"),
    path("donatori/", views.DonatoreListView.as_view(), name="donatori"),
    path(
        "donatori/<int:pk>/",
        views.DonatoreDetailView.as_view(),
        name="donatore",
    ),
    path(
        "donatori/add-stampa/<int:pk>/",
        views.donatore_add_stampa,
        name="donatore-add-stampa",
    ),
    path(
        "donatori/remove-stampa/",
        views.donatore_remove_stampa,
        name="donatore-remove-stampa",
    ),
    path(
        "donatori/remove-stampa/<int:pk>/",
        views.donatore_remove_stampa,
        name="donatore-remove-stampa",
    ),
    path(
        "donatori/<int:pk>/nuova-donazione/",
        views.DonazioneCreateView.as_view(),
        name="donazione-create",
    ),
]
