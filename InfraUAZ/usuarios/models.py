from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, contrasena=None, **extra_fields):
        if not correo:
            raise ValueError("Debe tener un correo")
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre=nombre, **extra_fields)
        user.set_password(contrasena)
        is_staff = extra_fields.get('is_staff', False)
        if not is_staff:
            user.is_active = False
            user.verificado = False
        user.save(using=self._db)
        return user
    
    def create_staff_user(self, correo, nombre, contrasena=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('verificado', True)
        return self.create_user(correo, nombre, contrasena, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, max_length=100)
    verificado = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre"]

    def __str__(self):
        return self.nombre

class Denunciante(models.Model):
    id_denunciante = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='denunciante')

class Administrador(models.Model):
    id_administrador = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='administrador')
    programa_academico = models.OneToOneField('denuncias.ProgramaAcademico', on_delete=models.RESTRICT)
