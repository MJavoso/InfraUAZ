# Importación para generar PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import inch
# Importaciones para poner la fecha en el título PDF
from datetime import datetime
from io import BytesIO
# Importar el modelo Denuncia, render y el administrador
from django.http import HttpRequest, HttpResponse
from usuarios.models import Administrador
from denuncias.models import Denuncia, EstadoDenuncia, TipoDenuncia
from django.shortcuts import render, redirect
# ListView para la bandeja de entrada
from django.views.generic import ListView
# Importación para asegurarse que el usuario se loguee
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
# Importación que asegura que solo los administradores accedan
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q

# Vista para la bandeja de entrada del administrador
class BandejaEntradaAdminListView(LoginRequiredMixin, ListView):
    model = Denuncia
    template_name = 'administrador/bandeja_entrada_admin.html'
    context_object_name = 'denuncias'
    paginate_by = 10

    def get_queryset(self):
        usuario = self.request.user

        # Si no es administrador o no tiene edificio asignado
        if not (usuario.is_staff and hasattr(usuario, 'administrador')):
            return Denuncia.objects.none()

        admin = usuario.administrador

        # Denuncias del edificio del administrador
        queryset = Denuncia.objects.filter(
            id_lugar__id_programa__id_edificio=admin.programa_academico.id_edificio
        ).select_related('id_estado', 'id_tipo_denuncia', 'id_lugar').order_by('-fecha')

        # Capturamos los filtros GET
        id_tipo_denuncia = self.request.GET.get('tipo_denuncia')
        id_estado = self.request.GET.get('estado')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        # 🔹 Aplicamos los filtros si existen
        if id_tipo_denuncia:
            queryset = queryset.filter(id_tipo_denuncia=id_tipo_denuncia)
        if id_estado:
            queryset = queryset.filter(id_estado=id_estado)
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        elif fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        elif fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)

        return queryset

    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto para las tarjetas y filtros."""
        context = super().get_context_data(**kwargs)
        denuncias_admin = self.get_queryset()

        # Datos para los filtros
        context['tipo_denuncia'] = TipoDenuncia.objects.all()
        context['estado_denuncia'] = EstadoDenuncia.objects.all()

        # Contadores actualizados según el queryset filtrado
        context['total_denuncias'] = denuncias_admin.count()
        context['cant_pendientes'] = denuncias_admin.filter(id_estado = 1).count()
        context['cant_revision'] = denuncias_admin.filter(id_estado = 2).count()
        context['cant_resueltas'] = denuncias_admin.filter(id_estado = 3).count()

        # Mantiene los filtros seleccionados
        context['filtros'] = self.request.GET

        return context


@login_required
def bandeja_entrada_admin(request: HttpRequest):
    denuncias = Denuncia.objects.all()
    tipo = TipoDenuncia.objects.all()
    estado = EstadoDenuncia.objects.all()
    total = denuncias.count()
    if request.method == 'POST':
        id_tipo_denuncia = request.POST.get('tipo_denuncia')
        id_estado = request.POST.get('estado')
        fechai = request.POST.get('fechai')
        fechaf = request.POST.get('fechaf')
        if id_tipo_denuncia:
            denuncias = denuncias.filter(id_tipo_denuncia=id_tipo_denuncia)
        if id_estado :
            denuncias = denuncias.filter(id_estado = id_estado)
        if fechai and fechaf:
            denuncias = denuncias.filter(fecha__range=(fechai, fechaf))
        elif fechai:
            denuncias = denuncias.filter(fecha__gte=fechai)   # Desde fecha inicial
        elif fechaf:
            denuncias = denuncias.filter(fecha__lte=fechaf)   # Hasta fecha final
    else:
        denuncias.order_by('-fecha')
    paginator = Paginator(denuncias, 5)  
    page_number = request.GET.get('page') 
    denuncias_paginadas = paginator.get_page(page_number) 
    cant_pendientes = Denuncia.objects.filter(id_estado = 1).count()
    cant_revision = Denuncia.objects.filter(id_estado = 2).count()
    cant_resueltas = Denuncia.objects.filter(id_estado = 3).count()
    context = {'total':total,'denuncias':denuncias, 'tipo_denuncia':tipo, 'denuncias_paginadas':denuncias_paginadas,'estado_denuncia':estado,'cant_pendientes':cant_pendientes, 'cant_revision':cant_revision, 'cant_resueltas':cant_resueltas, 'filtros':request.POST}


    return render(request, 'bandeja_entrada_admin.html', context)

# Vista para el panel de administrador

@login_required
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


# Vista para generar el PDF del botón 'reporte de denuncias'
@staff_member_required
def generar_reporte_denuncias_pdf(request):
    # Crear respuesta PDF
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"reporte_denuncias_{fecha_actual}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'

    buffer = BytesIO()

    # Configurar documento
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=60,
        bottomMargin=50,
    )

    elements = []
    styles = getSampleStyleSheet()

    # 🔹 Estilos personalizados
    title_style = ParagraphStyle(
        "TituloPrincipal",
        parent=styles["Title"],
        alignment=1,  # centrado
        fontSize=18,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        alignment=1,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "EncabezadoDenuncia",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#002855"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Cuerpo",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
    )

    # 🔹 Encabezado principal
    elements.append(Paragraph("Universidad Autónoma de Zacatecas", title_style))
    elements.append(Paragraph("Reporte de Denuncias - Campus Siglo XXI", subtitle_style))
    elements.append(
        Paragraph(
            f"<font size=9>Generado el {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</font>",
            subtitle_style,
        )
    )

    # 🔹 Obtener denuncias
    denuncias = Denuncia.objects.all().order_by("-fecha")

    # 🔹 Recorrer denuncias
    for idx, denuncia in enumerate(denuncias, start=1):
        elements.append(Paragraph(f"Denuncia #{idx}: {denuncia.título}", heading_style))
        elements.append(Spacer(1, 5))

        # Información básica
        info_data = [
            ["Denunciante:", denuncia.id_denunciante.usuario.nombre if denuncia.id_denunciante else "—"],
            ["Tipo de denuncia:", denuncia.id_tipo_denuncia.descripcion if denuncia.id_tipo_denuncia else "—"],
            ["Estado:", denuncia.id_estado.estado if denuncia.id_estado else "—"],
            ["Fecha:", denuncia.fecha.strftime("%d/%m/%Y")],
        ]
        info_table = Table(info_data, colWidths=[130, 380])
        info_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 6))

        # Descripción
        elements.append(Paragraph("<b>Descripción:</b>", body_style))
        elements.append(Paragraph(denuncia.descripcion, body_style))
        elements.append(Spacer(1, 10))

        # 🔹 Tabla de insumos con precios
        if hasattr(denuncia, "insumo_set") and denuncia.insumo_set.exists():
            elements.append(Paragraph("<b>Insumos utilizados:</b>", body_style))

            insumos_data = [["Nombre", "Cantidad", "Precio Unitario ($)", "Total Parcial ($)"]]
            total_general = 0

            for insumo in denuncia.insumo_set.all():
                precio_unitario = getattr(insumo, "costo", 0)
                total_parcial = precio_unitario * insumo.cantidad
                total_general += total_parcial

                insumos_data.append([
                    insumo.nombre,
                    str(insumo.cantidad),
                    f"${precio_unitario:.2f}",
                    f"${total_parcial:.2f}",
                ])

            # Agregamos fila final con el total general
            insumos_data.append([
                "",
                "",
                Paragraph("<b>Total General</b>", body_style),
                Paragraph(f"<b>${total_general:.2f}</b>", body_style),
            ])

            insumos_table = Table(insumos_data, colWidths=[200, 100, 100, 100])
            insumos_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#002855")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.whitesmoke, colors.lightgrey]),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e9ecef")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]))

            elements.append(insumos_table)
        else:
            elements.append(
                Paragraph("<i>No hay insumos registrados para esta denuncia.</i>", body_style)
            )

        elements.append(Spacer(1, 20))
        elements.append(
            Table(
                [[""]],
                colWidths=[500],
                style=[
                    ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.grey),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ],
            )
        )
        elements.append(PageBreak())

    # 🔹 Función para número de página
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        page_number = canvas.getPageNumber()
        text = f"Página {page_number}"
        canvas.drawCentredString(letter[0] / 2, 0.6 * inch, text)
        canvas.restoreState()

    # 🔹 Generar PDF
    pdf.build(elements, onFirstPage=footer, onLaterPages=footer)

    pdf_value = buffer.getvalue()
    buffer.close()
    response.write(pdf_value)
    return response

# Vista para el perfil del administrador
@login_required
def perfil_administrador(request):
    admin = Administrador.objects.filter(usuario=request.user).first()

    if not admin:
        return render(request, 'administrador/perfil_admin.html', {
            'error': 'No tienes asignado un programa académico o no eres administrador registrado.'
        })

    edificio = admin.programa_academico.id_edificio

    # Obtenemos las denuncias del edificio correspondiente al administrador
    denuncias = Denuncia.objects.filter(
        id_lugar__id_programa__id_edificio=edificio
    ).order_by('-fecha')

    # Filtramos los campos de los filtros
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

    # Paginación de 10 denuncias por página
    paginator = Paginator(denuncias, 10)
    page_number = request.GET.get('page')
    denuncias_paginadas = paginator.get_page(page_number)

    # Contadores de los tipops de denuncia
    total = denuncias.count()
    pendientes = denuncias.filter(id_estado=1).count()
    en_revision = denuncias.filter(id_estado=2).count()
    resueltas = denuncias.filter(id_estado=3).count()
    canceladas = denuncias.filter(id_estado=4).count()

    contexto = {
        'admin': admin,
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

    return render(request, 'administrador/perfil_admin.html', contexto)
