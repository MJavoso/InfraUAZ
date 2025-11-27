from django.urls import path
from . import views
from denuncias.views import ListView, perfil

urlpatterns = [
    # Ruta para la vista de la bandeja de entrada del administrador
    path('', ListView.as_view(), name='muro_denuncia'),
    # Ruta para la vista del panel de administrador
    path('panel-administrador/', views.panel_administrador, name='panel_administrador'),
    # Ruta para la vista del perfil del administrador
    path('perfil/', perfil, name='perfil'),
    # Ruta para filtrar denuncias del panel de denuncias
    path("administrador/filtrar-denuncias/", views.filtrar_denuncias_panel, name="filtrar_denuncias_panel"),
]