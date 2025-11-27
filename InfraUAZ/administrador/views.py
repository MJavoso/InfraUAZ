from django.http import HttpResponse
from django.http import HttpRequest, HttpResponse
from usuarios.models import Administrador
from denuncias.models import Denuncia, EstadoDenuncia, TipoDenuncia
from django.shortcuts import render, redirect
# ListView para la bandeja de entrada
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from usuarios.utils import administrador_required

# Vista para el panel de administrador
@administrador_required
def panel_administrador(request):
    usuario = request.user
    admin = Administrador.objects.filter(usuario=usuario).first()
    # Si no es administrador
    if not admin:
        return render(request, 'administrador/panel.html', {
            'error': 'No tienes asignado un programa académico o no eres administrador registrado.'
        })

    edificio = admin.programa_academico.id_edificio
    # Obtenemos las denuncias correspondientes al edificio del administrador
    denuncias = Denuncia.objects.filter(
        id_lugar__id_programa__id_edificio=edificio
    ).order_by('-fecha')

    # Filtros GET
    tipo = request.GET.get('tipo_denuncia')
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if tipo:
        denuncias = denuncias.filter(id_tipo_denuncia=tipo)
    if estado:
        denuncias = denuncias.filter(id_estado=estado)
    if fecha_inicio and fecha_fin:
        denuncias = denuncias.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        denuncias = denuncias.filter(fecha__gte=fecha_inicio)
    elif fecha_fin:
        denuncias = denuncias.filter(fecha__lte=fecha_fin)

    # Paginación (10 denuncias por página)
    paginator = Paginator(denuncias, 10)
    page_number = request.GET.get('page')
    denuncias_paginadas = paginator.get_page(page_number)

    # Contadores por estado
    total = denuncias.count()
    pendientes = denuncias.filter(id_estado=1).count()
    en_revision = denuncias.filter(id_estado=2).count()
    resueltas = denuncias.filter(id_estado=3).count()
    canceladas = denuncias.filter(id_estado=4).count()

    contexto = {
        'denuncias': denuncias_paginadas,
        'tipo_denuncia': TipoDenuncia.objects.all(),
        'estado_denuncia': EstadoDenuncia.objects.all(),
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'resueltas': resueltas,
        'canceladas': canceladas,
        'edificio': edificio,
        'filtros': request.GET
    }

    return render(request, 'administrador/panel.html', contexto)

# Vista para filtrar las denuncias del panel de denuncias en tiempo real
@administrador_required
def filtrar_denuncias_panel(request):
    # Obtener el usuario actual
    usuario = request.user

    # Validar que sea administrador
    admin = Administrador.objects.filter(usuario=usuario).first()
    if not admin:
        return HttpResponse("No autorizado", status=403)

    # Obtener el edificio asignado al administrador
    edificio = admin.programa_academico.id_edificio

    # Obtener filtros enviados por AJAX
    estado = request.GET.get("estado")
    tipo = request.GET.get("tipo")
    busqueda = request.GET.get("busqueda", "").strip()

    # Filtrar denuncias por edificio
    denuncias = Denuncia.objects.filter(
        id_lugar__id_programa__id_edificio=edificio
    ).select_related("id_estado", "id_tipo_denuncia", "id_denunciante", "id_lugar")

    # Aplicar filtros dinámicos
    if estado:
        denuncias = denuncias.filter(id_estado=estado)
    if tipo:
        denuncias = denuncias.filter(id_tipo_denuncia=tipo)
    if busqueda:
        denuncias = denuncias.filter(
            Q(título__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(id_lugar__nombre_lugar__icontains=busqueda)
            | Q(id_denunciante__usuario__nombre__icontains=busqueda)
        )

    # Renderizar solo la tabla actualizada
    return render(request, "administrador/tabla_denuncias.html", {"denuncias": denuncias})

