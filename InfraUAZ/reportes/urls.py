from django.urls import path
from .views import generar_reporte_denuncias_pdf
 
urlpatterns = [
    path("reporte-denuncias-pdf/", generar_reporte_denuncias_pdf, name="reporte_denuncias_pdf",),
]
