from django.shortcuts import render
from django.http import HttpRequest
from .forms import DenuncianteForm
from django.contrib import messages
from .forms import AdministradorForm

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


#agregar administrador
def registro_admin(request):
    if request.method == "POST":
        form = AdministradorForm(request.POST)
        if form.is_valid():
            # Guardar el administrador
            form.save()
            messages.success(request, "Administrador agregado correctamente")
            form = AdministradorForm()  # Limpiar el formulario
        else:
            messages.error(request, "Por favor corrige los errores del formulario")
    else:
        form = AdministradorForm()

    return render(request, 'registro_admin.html', {'form': form})