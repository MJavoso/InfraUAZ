from django.urls import path
from . import views

urlpatterns = [
    path('', views.muro_denuncias, name='muro_denuncias'),
    path('crear-denuncia', views.crear_denuncia, name='crear_denuncia'),
    path('programas/<int:id_edificio>/', views.filtrar_programas_por_edificio, name='filtrar_programas_por_edificio'),
    path('lugar_referencia/<int:id_programa>/<int:id_tipolugar>/', views.lugar_referencia, name='lugar_referencia'),
]