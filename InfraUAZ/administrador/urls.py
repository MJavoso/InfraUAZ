from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_administrador, name='panel_administrador'),
]
