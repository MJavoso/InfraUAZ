from django.urls import path
from . import views

urlpatterns = [
    path('', views.muro_denuncias, name='muro_denuncias'),
    path('crear-denuncia', views.crear_denuncia, name='crear_denuncia')
]