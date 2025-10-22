from django.urls import path
from . import views

urlpatterns = [
    path('', views.muro_denuncias, name='muro_denuncias'),
]