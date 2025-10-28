from django.urls import path
from . import views

urlpatterns = [
    path('crear-cuenta', views.registrar_denunciante, name='crear_cuenta_denunciante'),
    path('login', views.login, name='login'),
    path('login/denunciante', views.login_denunciante, name='login_denunciante'),
    path('login/administrador', views.login_administrador, name='login_administrador'),
    path('logout', views.logout, name='logout'),
    path('activar/<slug:uidb64>/<slug:token>', views.activar_cuenta, name='activar_cuenta'),
    path('crear-cuenta/correo/<slug:uidb64>', views.reenviar_correo_activacion, name='reenviar_correo'),
    path('registro-admin/', views.registro_admin, name='registro_admin'),
]