from os import environ
from django import setup as django_setup

environ.setdefault('DJANGO_SETTINGS_MODULE', 'InfraUAZ.settings')
django_setup()

from usuarios.models import Usuario, Administrador
from denuncias.models import ProgramaAcademico

__DEFAULT_PROGRAMA_ID = 2 # Ingeniería de software de acuerdo a los fixtures

def create_default_admin():
    correo = "infrauaz@uaz.edu.mx"
    nombre = "Administrador provisional"
    contrasena = "infrauaz_admin.ingsoft$"

    if not Usuario.objects.filter(correo=correo).exists():
        usuario = Usuario.objects.create_staff_user(
            correo=correo,
            nombre=nombre,
            contrasena=contrasena
        )

        programa = ProgramaAcademico.objects.filter(pk=2).first()

        administrador = Administrador.objects.create(usuario=usuario, programa_academico=programa)
        if administrador:
            print("Se creó el administrador por defecto")
        

if __name__ == '__main__':
    create_default_admin()