from django.urls import path
from . import views

urlpatterns = [
    path('', views.DenunciasListView.as_view(), name='muro_denuncias'),
    path('crear-denuncia', views.crear_denuncia, name='crear_denuncia'),
    # El <int:id_denuncia> hace que la url muestre el id de la denuncia 
    # despues del nombre de la ruta, por ejemplo: /detalle-denuncia/5/--> 5 es el id de la denuncia
    path('detalle-denuncia/<int:id_denuncia>/', views.detalle_denuncia, name='detalle_denuncia'),
    path('denuncia/<int:id_denuncia>/agregar-insumo/', views.agregar_insumo, name='agregar_insumo'),
    path('filtrar_denuncia/<int:id_tipo_denuncia>/<int:id_estado>/<str:fechai>/<str:fechaf>/', views.filtrar_denuncia, name="filtrar_denuncia"),
    path('programas/<int:id_edificio>/', views.filtrar_programas_por_edificio, name='filtrar_programas_por_edificio'),
    path('lugar_referencia/<int:id_programa>/<int:id_tipolugar>/', views.lugar_referencia, name='lugar_referencia'),
]