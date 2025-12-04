from django.shortcuts import render
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.units import inch
from django.db.models import Q
# Importaciones para poner la fecha en el título PDF
from datetime import datetime
from io import BytesIO
from denuncias.models import Denuncia
from usuarios.utils import administrador_required
# Vista para generar el PDF del botón 'reporte de denuncias'
@administrador_required
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
    edificio = int(request.GET.get("edificio"))
    
    denuncias = Denuncia.objects.filter(
        id_lugar__id_programa__id_edificio=edificio
    ).order_by('-fecha')
    
    estado = request.GET.get("estado")
    tipo = request.GET.get("tipo")
    busqueda = request.GET.get("busqueda", "").strip()

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
            ["Lugar de referencia:", denuncia.id_lugar.nombre_lugar if denuncia.id_lugar else "—" ],
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
