from django.shortcuts import render
from django.http import HttpRequest
from .forms import DenuncianteForm

def registrar_denunciante(request: HttpRequest):
    form = DenuncianteForm()
    creado = False
    if request.method == 'POST':
        form = DenuncianteForm(request.POST)
        if form.is_valid():
            denunciante = form.save()
            creado = True
            # TODO: Enviar correo de verificación
    context = {
        'denunciante_form': form,
        'creado': creado
    }
    return render(request, 'crear_cuenta_denunciante.html', context=context)