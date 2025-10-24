from django.urls import path
from . import views

urlpatterns = [
    path('crear-cuenta', views.registrar_denunciante, name='crear_cuenta_denunciante'),
    path('registro-admin/', views.registro_admin, name='registro_admin')
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
]