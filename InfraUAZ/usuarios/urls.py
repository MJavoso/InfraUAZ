from django.urls import path, include
from . import views

_usuarios_urls = [
    path('admins/lista', views.lista_admins, name='lista_admins'),
    path('admin/detalle/<int:id_admin>', views.detalle_admin, name='detalle_admin'),
    path('actualizar-info-admin', views.actualizar_info_admin, name='actualizar_info_admin'),
]

urlpatterns = [
    path('crear-cuenta', views.registrar_denunciante, name='crear_cuenta_denunciante'),
    path('login', views.login, name='login'),
    path('login/denunciante', views.login_denunciante, name='login_denunciante'),
    path('login/administrador', views.login_administrador, name='login_administrador'),
    path('logout', views.logout, name='logout'),
    path('activar/<slug:uidb64>/<slug:token>', views.activar_cuenta, name='activar_cuenta'),
    path('crear-cuenta/correo/<slug:uidb64>', views.reenviar_correo_activacion, name='reenviar_correo'),
    path('usuarios/', include(_usuarios_urls)),
]