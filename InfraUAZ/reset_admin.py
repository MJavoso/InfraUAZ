from os import environ
from django import setup as django_setup

environ.setdefault('DJANGO_SETTINGS_MODULE', 'InfraUAZ.settings')
django_setup()

from usuarios.models import Usuario, Administrador

def create_default_admin():
    correo = "infrauaz@uaz.edu.mx"
    contrasena = environ.get('ADMIN_DEFAULT_PASSWORD')

    usuario = Usuario.objects.filter(correo=correo).first()
    if usuario:
        usuario.set_password(contrasena)
        usuario.save()
        print("Se actualizó la contraseña del administrador por defecto")
    else:
        print("No se encontró el administrador por defecto")

if __name__ == '__main__':
    create_default_admin()