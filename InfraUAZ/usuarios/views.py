from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import DenuncianteForm, LoginForm, AdministradorForm
from django.forms.forms import ValidationError
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .models import Usuario, Denunciante
from .utils import es_administrador, enviar_correo_activacion, activar_cuenta_denunciante, EmailStatus


def registrar_denunciante(request: HttpRequest):
    # Función interna de registrar_denunciante para redireccionar a la ventana de estado_envio_correo.html
    def redireccion_fallo(id_denunciante):
        context = {
            'estado': EmailStatus.EMAIL_FAILED.value,
            'uidb64': urlsafe_base64_encode(force_bytes(id_denunciante))
        }
        return render(request, 'estado_envio_correo.html', context=context)
    
    def redireccion_formulario(form):
        context = {
            'denunciante_form': form
        }
        return render(request, 'crear_cuenta_denunciante.html', context=context)

    form = DenuncianteForm()
    if request.method == 'GET':
        print("Peticion de formulario")
        return redireccion_formulario(form)
    
    form = DenuncianteForm(request.POST)
    if not form.is_valid():
        print("El formulario no es valido")
        return redireccion_formulario(form)

    try:
        usuario, denunciante = form.save()
    except ValidationError as e:
        if e.code == "user_exists":
            print("El denunciante ya existe")
            id_denunciante = e.params.get('denunciante_id')
            return redireccion_fallo(id_denunciante)
        else:
            print("Hay un error al guardar al usuario:", e.message)
            form.add_error(None, e.message)
            print(form)
            return redireccion_formulario(form)

    resultado = enviar_correo_activacion(
        dominio=get_current_site(request).domain,
        correo=usuario.correo,
        nombre=usuario.nombre,
        denunciante=denunciante,
        usuario=usuario
    ) 

    if resultado:
        context = {
            'estado': EmailStatus.EMAIL_SENT.value,
            'correo': usuario.correo,
            'uidb64': urlsafe_base64_encode(force_bytes(denunciante.id_denunciante))
        }
        print("Se envió el correo")
        return render(request, 'estado_envio_correo.html', context=context)
    else:
        print("Error al enviar el correo")
        return redireccion_fallo(denunciante.id_denunciante)


def registro_admin(request):
    if request.method == "POST":
        form = AdministradorForm(request.POST)
        if form.is_valid():
            form.save()  # <-- ahora hace todo internamente
            messages.success(request, "Administrador agregado correctamente.")
            return redirect('registro_admin')
        else:
            messages.error(
                request, "Por favor corrige los errores del formulario.")
    else:
        form = AdministradorForm()

    return render(request, 'registro_admin.html', {'form': form})

def reenviar_correo_activacion(request: HttpRequest, uidb64: int):
    id_denunciante = int(urlsafe_base64_decode(uidb64))
    denunciante = Denunciante.objects.get(pk=id_denunciante)
    usuario = denunciante.usuario
    if usuario.is_active:
        context = {
            'estado': EmailStatus.USER_ACTIVE.value,
        }
        return render(request, 'estado_envio_correo.html', context=context)

    resultado = enviar_correo_activacion(
        dominio=get_current_site(request).domain,
        correo=usuario.correo,
        nombre=usuario.nombre,
        denunciante=denunciante,
        usuario=usuario
    )
    if resultado:
        context = {
            'estado': EmailStatus.EMAIL_SENT.value,
            'correo': usuario.correo
        }
        return render(request, 'estado_envio_correo.html', context=context)
    else:
        context = {
            'estado': EmailStatus.EMAIL_FAILED.value,
            'uidb64': urlsafe_base64_encode(force_bytes(denunciante.id_denunciante))
        }
        return render(request, 'estado_envio_correo.html', context=context)

def activar_cuenta(request: HttpRequest, uidb64, token):
    resultado = activar_cuenta_denunciante(uid=uidb64, token=token)
    context = {
            'estado': resultado.value
    }
    return render(request, 'estado_envio_correo.html', context=context)

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
