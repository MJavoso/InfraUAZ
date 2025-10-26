from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import DenuncianteForm, LoginForm
from .models import Usuario
from .utils import es_administrador
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
            return redirect('login')
    context = {
        'denunciante_form': form,
        'creado': creado
    }
    return render(request, 'crear_cuenta_denunciante.html', context=context)

def login(request: HttpRequest):
    return render(request, 'login.html')

def login_denunciante(request: HttpRequest):
    form = LoginForm()
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            contrasena = form.cleaned_data["contrasena"]
            try:
                usuario = Usuario.objects.get(correo=correo)
                if usuario.check_password(contrasena):
                    auth_login(request, usuario)
                    return redirect('muro_denuncias')
                else:
                    error = "Correo o contraseña incorrectos"
            except Usuario.DoesNotExist:
                error = "Correo o contraseña incorrectos"
    context = {
        "form": form,
        "error": error
    }
    return render(request, 'login_denunciante.html', context=context)


def login_administrador(request: HttpRequest):
    form = LoginForm()
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data["correo"]
            contrasena = form.cleaned_data["contrasena"]
            try:
                usuario = Usuario.objects.get(correo=correo)
                if usuario.check_password(contrasena) and es_administrador(usuario.id):
                    auth_login(request, usuario)
                    return redirect('muro_denuncias')
                else:
                    error = "Correo o contraseña incorrectos"
            except Usuario.DoesNotExist:
                error = "Correo o contraseña incorrectos"
    context = {
        "form": form,
        "error": error
    }
    return render(request, 'login_administrador.html', context=context)


def logout(request):
    auth_logout(request)
    return redirect('login')

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
