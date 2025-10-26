from .models import Administrador

def es_administrador(id_usuario: int):
    return Administrador.objects.filter(pk=id_usuario).exists()