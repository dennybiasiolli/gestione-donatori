from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import forms, views

router = DefaultRouter()
router.register("donatori", views.DonatoreViewSet)

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
        "donatori/check-privacy/<int:pk>/",
        views.donatore_check_privacy,
        name="donatore-check-privacy",
    ),
    path(
        "donatori/uncheck-privacy/<int:pk>/",
        views.donatore_uncheck_privacy,
        name="donatore-uncheck-privacy",
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
    path(
        "dati-statistici/",
        views.dati_statistici,
        name="dati-statistici",
    ),
    path(
        "export-elenco-soci/",
        views.export_elenco_soci,
        name="export-elenco-soci",
    ),
]
