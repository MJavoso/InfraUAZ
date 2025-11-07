from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render

from usuarios.models import Denunciante
from .forms import DenunciaForm
from .models import ProgramaAcademico, LugarReferencia, Denuncia, Insumo, TipoDenuncia, EstadoDenuncia
from django.http import JsonResponse
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator
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


@login_required
def crear_denuncia (request: HttpRequest):
    denuncia_form = DenunciaForm()
    if request.method == 'POST':
        denuncia_form = DenunciaForm(request.POST)
        id_programa = request.POST.get('programa')
        id_lugar = request.POST.get('lugarReferencia')
        # en esta parte actualizo el queryset de mi formulario, ya que todavia esta none(), por que hago el filtrado en views
        if id_programa:
            denuncia_form.fields['programa'].queryset = ProgramaAcademico.objects.filter(id_programa=id_programa)
        if id_lugar:
            denuncia_form.fields['lugarReferencia'].queryset = LugarReferencia.objects.filter(id_lugar=id_lugar)
        if denuncia_form.is_valid():
            denuncia_form.save(request.user)
            return redirect('muro_denuncias')
        else:
            print(denuncia_form.errors)
    context = {'denuncia_form':denuncia_form}
    return render(request, 'crear_denuncia.html',context)

def filtrar_programas_por_edificio(request, id_edificio):
    programas = ProgramaAcademico.objects.filter(id_edificio_id=id_edificio)
    data = [{"id": p.id_programa, "nombre": p.nombre_programa} for p in programas]
    return JsonResponse(data, safe=False)

def lugar_referencia(request, id_programa, id_tipolugar):
    lugares_referencia = LugarReferencia.objects.filter(
        id_programa_id=id_programa,
        id_tipo_id=id_tipolugar
    )
    data = [{"id": lr.id_lugar, "nombre": lr.nombre_lugar} for lr in lugares_referencia]
    return JsonResponse(data, safe=False)

class DenunciasListView(ListView):
    model=Denuncia
    template_name = 'muro_denuncias.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tipo_denuncia'] = TipoDenuncia.objects.all()
        context['estado_denuncia'] = EstadoDenuncia.objects.all()
        context['cant_pendientes'] = Denuncia.objects.filter(id_estado = 1).count()
        context['cant_revision'] = Denuncia.objects.filter(id_estado = 2).count()
        context['cant_resueltas'] = Denuncia.objects.filter(id_estado = 3).count()


        return context

@login_required
def muro_denuncias(request: HttpRequest):
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


    return render(request, 'muro_denuncias.html', context)

@login_required
def perfil(request:HttpRequest ): 

    id_denunciante =  Denunciante.objects.get(usuario=request.user).id_denunciante 
    denuncias = Denuncia.objects.filter(id_denunciante=id_denunciante)
    tipos = TipoDenuncia.objects.all()
    estados = EstadoDenuncia.objects.all()

    total = denuncias.count()
    cant_pendientes = denuncias.filter(id_estado = 1).count()
    cant_revision = denuncias.filter(id_estado = 2).count()
    cant_resueltas = denuncias.filter(id_estado = 3).count()
    cant_canceladas = denuncias.filter(id_estado = 4).count()

    if request.method == 'POST':
        id_tipo_denuncia = request.POST.get('tipo_denuncia')
        id_estado = request.POST.get('estado_denuncia')

        if id_tipo_denuncia:
            denuncias = denuncias.filter(id_tipo_denuncia=id_tipo_denuncia)
        if id_estado :
            denuncias = denuncias.filter(id_estado = id_estado)
    else:
        denuncias.order_by('-fecha')
    context = {
        'denuncias':denuncias,
        'tipos': tipos,
        'estados' : estados,
        'total':total,
        'cant_pendientes':cant_pendientes,
        'cant_revision':cant_revision,
        'cant_resueltas':cant_resueltas,
        'cant_canceladas':cant_canceladas,
        'filtros':request.POST

    }
    return render (request,'perfil.html', context)
def modal_denuncia(request):
    #Despues se procesaran datos aqui
    return render(request, 'modal_denuncia.html')
