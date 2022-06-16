from django.contrib.auth import views as auth_views
from django.urls import path, include

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('donatori/', views.donatori, name='donatori'),
    path('donatori/<int:pk>/', views.donatore, name='donatore'),
]
