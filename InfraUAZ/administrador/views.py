from django.shortcuts import render
from denuncias.models import Denuncia  # Asegúrate de tener este modelo importado

def panel_administrador(request):
    # Obtener denuncias pendientes por defecto
    denuncias = Denuncia.objects.filter(id_estado__estado='Pendiente')

    # Contadores de las denuncias por estado para poner en las tarjetas del panel
    total = Denuncia.objects.count()
    pendientes = Denuncia.objects.filter(id_estado__estado='Pendiente').count()
    en_revision = Denuncia.objects.filter(id_estado__estado='En revisión').count()
    resueltas = Denuncia.objects.filter(id_estado__estado='Resuelta').count()
    canceladas = Denuncia.objects.filter(id_estado__estado='Cancelada').count()

    # Contexto para pasar a la plantilla
    contexto = {
        'denuncias': denuncias,
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'resueltas': resueltas,
        'canceladas': canceladas,
    }
    # Renderizar la plantilla del panel con el contexto
    return render(request, 'panel.html', contexto)
