from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_administrador, name='panel_administrador'),
    path('reporte/pdf/', views.generar_reporte_denuncias_pdf, name='reporte_denuncias_pdf'),
]
