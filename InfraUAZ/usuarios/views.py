from django.shortcuts import render
from django.http import HttpRequest
from .forms import DenuncianteForm
from django.contrib import messages
from .forms import AdministradorForm
from django.shortcuts import render, redirect

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

def registro_admin(request):
    if request.method == "POST":
        form = AdministradorForm(request.POST)
        if form.is_valid():
            form.save()  # <-- ahora hace todo internamente
            messages.success(request, "Administrador agregado correctamente.")
            return redirect('registro_admin')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = AdministradorForm()

    return render(request, 'registro_admin.html', {'form': form})

#k