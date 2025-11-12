from django.urls import path
from . import views

urlpatterns = [
    # Ruta para la vista de la bandeja de entrada del administrador
    path('', views.BandejaEntradaAdminListView.as_view(), name='bandeja_entrada_administrador'),
    # Ruta para la vista del panel de administrador
    path('panel-administrador/', views.panel_administrador, name='panel_administrador'),
    # Ruta para la vista del perfil del administrador
    path('perfil/', views.perfil_administrador, name='perfil_admin'),
    # Ruta para generar el reporte de denuncias en PDF
    path('reporte/pdf/', views.generar_reporte_denuncias_pdf, name='reporte_denuncias_pdf'),
]