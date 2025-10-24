from django.shortcuts import render, get_object_or_404, redirect
from .models import Denuncia, Insumo

#------------------ Vista del muro de denuncias ------------------#
def muro_denuncias(request):
    # Obtener todas las denuncias con sus relaciones necesarias para evitar consultas adicionales
    denuncias = Denuncia.objects.select_related(
        # Incluir las relaciones necesarias para optimizar las consultas
        'id_estado', 
        'id_lugar__id_programa__id_edificio', 
        'id_tipo_denuncia'
    ).order_by('-fecha') # Ordenar por fecha descendente
    # Renderizar la plantilla con las denuncias obtenidas
    return render(request, 'muro_denuncias.html', {'denuncias': denuncias})

#------------------ Vista para crear una nueva denuncia ------------------#

def crear_denuncia(request):
    return render(request, 'crear_denuncia.html')

#------------------ Vista de detalle de denuncia ------------------#
def detalle_denuncia(request, id_denuncia):
    # Obtener la denuncia por su ID o devolver un error 404 si no existe
    denuncia = get_object_or_404(Denuncia, id_denuncia=id_denuncia)
    # Renderizar la plantilla con la denuncia obtenida
    return render(request, 'detalle_denuncia.html', {'denuncia':denuncia})

# Agrega un insumo en la plantilla detalle_denuncia.html
# en la parte de insumos
def agregar_insumo(request, id_denuncia):
    # Obtener la denuncia por su ID o devolver un error 404 si no existe
    denuncia = get_object_or_404(Denuncia, pk=id_denuncia)
    # Si el método de la solicitud es POST, procesa el formulario
    if request.method == "POST":
        # Datos del insumo desde el formulario
        nombre = request.POST.get("nombre")
        cantidad = request.POST.get("cantidad")
        costo = request.POST.get("costo")

        # Crear y guardar el nuevo insumo asociado a la denuncia
        Insumo.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            costo=costo,
            id_denuncia=denuncia
        )
    # Redirigir a la página de detalle de la denuncia después de agregar el insumo
    return redirect('detalle_denuncia', id_denuncia=id_denuncia)
