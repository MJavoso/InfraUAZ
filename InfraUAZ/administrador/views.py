from django.shortcuts import render
from denuncias.models import Denuncia, EstadoDenuncia

# Vista para el panel de administrador
def panel_administrador(request):
    # Obtener todas las denuncias y sus estados
    denuncias = Denuncia.objects.select_related('id_estado').all()

    # Calcular total de denuncias y el total de denuncias por estado
    total = denuncias.count()
    pendientes = denuncias.filter(id_estado__estado='Pendiente').count()
    en_revision = denuncias.filter(id_estado__estado='En revisión').count()
    resueltas = denuncias.filter(id_estado__estado='Resuelta').count()
    canceladas = denuncias.filter(id_estado__estado='Cancelada').count()
    # Preparar el contexto para el panel
    contexto = {
        'denuncias': denuncias,
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'resueltas': resueltas,
        'canceladas': canceladas,
    }
    # Renderizar el template del panel de administrador con el contexto
    return render(request, 'administrador/panel.html', contexto)
