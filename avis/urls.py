from django.urls import include, path

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('donatori/', views.donatori, name='donatori'),
    path('donatori/<int:pk>/', views.donatore, name='donatore'),
]
