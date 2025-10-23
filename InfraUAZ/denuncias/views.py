from django.shortcuts import render

# Create your views here.


def muro_denuncias(request):
    return render(request, 'muro_denuncias.html')

def crear_denuncia(request):
    return render(request, 'crear_denuncia.html')