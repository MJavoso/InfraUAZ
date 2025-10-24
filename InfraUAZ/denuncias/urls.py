from django.urls import path
from . import views

urlpatterns = [
    path('', views.muro_denuncias, name='muro_denuncias'),
    path('crear-denuncia', views.crear_denuncia, name='crear_denuncia'),
    # El <int:id_denuncia> hace que la url muestre el id de la denuncia 
    # despues del nombre de la ruta, por ejemplo: /detalle-denuncia/5/--> 5 es el id de la denuncia
    path('detalle-denuncia/<int:id_denuncia>/', views.detalle_denuncia, name='detalle_denuncia'),
    path('denuncia/<int:id_denuncia>/agregar-insumo/', views.agregar_insumo, name='agregar_insumo'),

]