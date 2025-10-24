from django.shortcuts import render
from .forms import DenunciaForm
from .models import TipoDenuncia, Edificio, TipoLugarReferencia, ProgramaAcademico, LugarReferencia
from django.http import JsonResponse
from django.http import HttpRequest
# Create your views here.


def muro_denuncias(request):
    return render(request, 'muro_denuncias.html')

def crear_denuncia(request: HttpRequest):
    denuncia_form = DenunciaForm()
    creado = False
    # if request.method == 'POST':
    #     denuncia_form = DenunciaForm(request.POST)
    #     if denuncia_form.is_valid():
    #         denuncia = denuncia_form.save()
    #         creado = True
    context = {'denuncia_form':denuncia_form, 'creado':creado}
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
