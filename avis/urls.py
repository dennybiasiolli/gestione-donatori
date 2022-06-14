from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('donatori/', views.donatori, name='donatori'),
    path('donatori/<int:pk>/', views.donatore, name='donatore'),
]
