# Importacion para generar PDF
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# Importaciones para poner la fecha en el título PDF
from datetime import datetime
from io import BytesIO
# Importar el modelo Denuncia y render
from denuncias.models import Denuncia
from django.shortcuts import render

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

# Vista para generar el PDF del boton 'reporte de denuncias' 
def generar_reporte_denuncias_pdf(request):
    # Crear la respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_denuncias.pdf"'

    # Crear el documento PDF
    # SimpleDocTemplate sirve para crear documentos PDF simples
    registrar_Denuncia_PDF = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del reporte
    titlo_PDF = Paragraph("Reporte de Denuncias - UAZ Siglo XXI", styles['Title'])
    elements.append(titlo_PDF)
    elements.append(Spacer(1, 12))

    # Encabezados de la tabla
    titulo_Columnas_Denuncia = [["Título", "Denunciante", "Tipo", "Descripción", "Estado", "Fecha"]]

    # Agrega las denuncias a la tabla
    denuncias = Denuncia.objects.all().order_by('-fecha')
    for denuncia in denuncias:
        titulo_Columnas_Denuncia.append([
            denuncia.título,
            denuncia.id_denunciante.usuario.nombre if denuncia.id_denunciante else "—",
            denuncia.id_tipo_denuncia.descripcion if denuncia.id_tipo_denuncia else "—",
            denuncia.descripcion[:60] + "..." if len(denuncia.descripcion) > 60 else denuncia.descripcion,
            denuncia.id_estado.estado if denuncia.id_estado else "—",
            denuncia.fecha.strftime("%d/%m/%Y")
        ])

    # Crear tabla de denuncias
    tabla_Denuncias = Table(titulo_Columnas_Denuncia, repeatRows=1)
    # Estilo de la tabla
    tabla_Denuncias.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#002855")),  # Color de fondo igual al azul de la UAZ
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(tabla_Denuncias)
    registrar_Denuncia_PDF.build(elements)
    return response