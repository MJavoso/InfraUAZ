from django.urls import path
from . import views

urlpatterns = [
    path('', views.muro_denuncias, name='muro_denuncias'),
    path('crear-denuncia', views.crear_denuncia, name='crear_denuncia'),
    path('perfil', views.perfil, name='perfil'),
    # El <int:id_denuncia> hace que la url muestre el id de la denuncia 
    # despues del nombre de la ruta, por ejemplo: /detalle-denuncia/5/--> 5 es el id de la denuncia
    path('detalle-denuncia/<int:id_denuncia>/', views.detalle_denuncia, name='detalle_denuncia'), 
    # Nueva ruta para cambiar el estado de una denuncia en el detalle de la denuncia
    path('denuncia/<int:id_denuncia>/cambiar_estado/', views.cambiar_estado_denuncia, name='cambiar_estado_denuncia'),
    # Nueva ruta para agregar insumos a una denuncia en el detalle de la denuncia
    path('denuncia/<int:id_denuncia>/agregar-insumo/', views.agregar_insumo, name='agregar_insumo'),
    path('programas/<int:id_edificio>/', views.filtrar_programas_por_edificio, name='filtrar_programas_por_edificio'),
    path('lugar_referencia/<int:id_programa>/<int:id_tipolugar>/', views.lugar_referencia, name='lugar_referencia'),
    path('denuncia/', views.modal_denuncia, name='modal_denuncia'),
]