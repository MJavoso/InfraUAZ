# Importación para generar PDF
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
# Importaciones para poner la fecha en el título PDF
from datetime import datetime
from io import BytesIO
# Importar el modelo Denuncia, render y el administrador
from usuarios.models import Administrador
from denuncias.models import Denuncia, EstadoDenuncia, TipoDenuncia
from django.shortcuts import render, redirect
# ListView para la bandeja de entrada
from django.views.generic import ListView
from django.urls import reverse_lazy
# Importación para asegurarse que el usuario se loguee
from django.contrib.auth.decorators import login_required
# Importación que asegura que solo los administradores accedan
from django.contrib.auth.mixins import LoginRequiredMixin

# Vista para la bandeja de entrada del administrador
class BandejaEntradaAdminListView(LoginRequiredMixin, ListView):
    model = Denuncia
    template_name = 'administrador/bandeja_entrada_admin.html'
    context_object_name = 'denuncias'
    paginate_by = 10  # si quieres paginación

    def get_queryset(self):
        """Filtra denuncias por el edificio asignado al administrador"""
        usuario = self.request.user
        if hasattr(usuario, 'administrador'):
            admin = usuario.administrador
            Denuncia.objects.filter(id_lugar__id_programa__id_edificio=admin.programa_academico.id_edificio)
            # Filtramos por el edificio del programa académico del admin
            return Denuncia.objects.filter(
                id_lugar__id_programa__id_edificio=admin.programa_academico.id_edificio
            ).select_related('id_estado', 'id_tipo_denuncia', 'id_lugar')
        return Denuncia.objects.none()

    def get_context_data(self, **kwargs):
        """Agrega los contadores y filtros al contexto"""
        context = super().get_context_data(**kwargs)
        # Agregar tipos de denuncia y estados al contexto para los filtros
        context['tipo_denuncia'] = TipoDenuncia.objects.all()
        context['estado_denuncia'] = EstadoDenuncia.objects.all()
        # Contadores de denuncias por estado
        context['cant_pendientes'] = Denuncia.objects.filter(id_estado__estado="Pendiente").count()
        context['cant_revision'] = Denuncia.objects.filter(id_estado__estado="En revisión").count()
        context['cant_resueltas'] = Denuncia.objects.filter(id_estado__estado="Resuelta").count()
        context['cant_canceladas'] = Denuncia.objects.filter(id_estado__estado="Cancelada").count()
        return context
    
# Vista para el panel de administrador
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
    return render(request, 'administrador/panel.html', contexto)


# Vista para generar el PDF del botón 'reporte de denuncias'
#@staff_member_required
def generar_reporte_denuncias_pdf(request):
    # Crear la respuesta HTTP con tipo PDF
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Nombre del archivo de reporte de denuncias con fecha incluida
    nombre_archivo = f"reporte_denuncias_{fecha_actual}.pdf"
    # HTTPResponse sirve para enviar el PDF como respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    # Crear el documento PDF
    buffer = BytesIO()
    registrar_Denuncia_PDF = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del reporte con fecha actual
    titulo_reporte = Paragraph(f"Reporte de Denuncias - UAZ Siglo XXI<br/><font size=10>Generado el {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</font>", styles['Title'])
    elements.append(titulo_reporte)
    elements.append(Spacer(1, 20))

    # Obtener todas las denuncias ordenadas por fecha descendente
    denuncias = Denuncia.objects.all().order_by('-fecha')

    # Generar una sección por denuncia
    for denuncia in denuncias:
        # Encabezado de denuncia
        elements.append(Paragraph(f"<b>Título:</b> {denuncia.título}", styles['Heading2']))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<b>Denunciante:</b> {denuncia.id_denunciante.usuario.nombre if denuncia.id_denunciante else '—'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Tipo de Denuncia:</b> {denuncia.id_tipo_denuncia.descripcion if denuncia.id_tipo_denuncia else '—'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Estado:</b> {denuncia.id_estado.estado if denuncia.id_estado else '—'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha:</b> {denuncia.fecha.strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Descripción:</b><br/>{denuncia.descripcion}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tabla de insumos asociados (si los hay)
        if hasattr(denuncia, 'insumo_set') and denuncia.insumo_set.exists():
            elements.append(Paragraph("<b>Insumos Utilizados:</b>", styles['Heading3']))
            datos_insumos = [["Nombre", "Cantidad", "Unidad"]]
            for insumo in denuncia.insumo_set.all():
                datos_insumos.append([
                    insumo.nombre,
                    str(insumo.cantidad),
                    insumo.unidad if hasattr(insumo, 'unidad') else "—",
                ])

            tabla_insumos = Table(datos_insumos, repeatRows=1)
            tabla_insumos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#002855")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]))
            elements.append(tabla_insumos)
        else:
            elements.append(Paragraph("<i>No hay insumos registrados para esta denuncia.</i>", styles['Normal']))

        # Salto de página para la siguiente denuncia
        elements.append(PageBreak())

    # Construir el PDF
    registrar_Denuncia_PDF.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

# Vista para el perfil del administrador
def perfil_administrador(request):
    # Obtener el administrador logueado
    admin = Administrador.objects.filter(usuario=request.user).first()

    if not admin:
        return render(request, 'administrador/perfil_admin.html', {
            'error': 'No tienes asignado un programa académico o no eres administrador registrado.'
        })

    # Edificio del programa académico del administrador
    edificio = admin.programa_academico.id_edificio

    # Denuncias del edificio asignado
    denuncias = Denuncia.objects.filter(
        id_lugar__id_programa__id_edificio=edificio
    ).order_by('-fecha')

    # Contadores
    total = denuncias.count()
    pendientes = denuncias.filter(id_estado__estado='Pendiente').count()
    en_revision = denuncias.filter(id_estado__estado='En revisión').count()
    resueltas = denuncias.filter(id_estado__estado='Resuelta').count()
    canceladas = denuncias.filter(id_estado__estado='Cancelada').count()

    contexto = {
        'admin': admin,
        'denuncias': denuncias,
        'total': total,
        'pendientes': pendientes,
        'en_revision': en_revision,
        'resueltas': resueltas,
        'canceladas': canceladas,
        'edificio': edificio,  # lo mandamos al template para mostrarlo
    }

    return render(request, 'administrador/perfil_admin.html', contexto)