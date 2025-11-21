from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http.response import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import DenuncianteForm, LoginForm, AdministradorForm, UpdateAdministradorForm, FiltrosListaAdminForm
from django.forms.forms import ValidationError
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Usuario, Denunciante, Administrador
from .utils import es_administrador, enviar_correo_activacion, activar_cuenta_denunciante, EmailStatus, administrador_required, obtener_dominio


def registrar_denunciante(request: HttpRequest):
    # Función interna de registrar_denunciante para redireccionar a la ventana de estado_envio_correo.html
    def redireccion_fallo(id_denunciante, estado=EmailStatus.EMAIL_FAILED):
        context = {
            'estado': estado.value,
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
            print("El denunciante ya existe", flush=True)
            id_denunciante = e.params.get('denunciante_id')
            return redireccion_fallo(id_denunciante, EmailStatus.USER_EXISTS)
        else:
            print("Hay un error al guardar al usuario:", e.message, flush=True)
            form.add_error(None, e.message)
            return redireccion_formulario(form)

    resultado = enviar_correo_activacion(
        dominio=obtener_dominio(request),
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

def reenviar_correo_activacion(request: HttpRequest, uidb64):
    id_denunciante = int(urlsafe_base64_decode(uidb64))
    denunciante = Denunciante.objects.get(pk=id_denunciante)
    usuario = denunciante.usuario
    if usuario.verificado:
        context = {
            'estado': EmailStatus.USER_ACTIVE.value,
        }
        return render(request, 'estado_envio_correo.html', context=context)

    resultado = enviar_correo_activacion(
        dominio=obtener_dominio(request),
        correo=usuario.correo,
        nombre=usuario.nombre,
        denunciante=denunciante,
        usuario=usuario
    )
    if resultado:
        context = {
            'estado': EmailStatus.EMAIL_SENT.value,
            'correo': usuario.correo,
            'uidb64': uidb64
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
                if usuario.is_active and usuario.check_password(contrasena):
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
                    return redirect('muro_denuncias')# Redirigir a la vista del administrador
                else:
                    error = "Correo o contraseña incorrectos"
            except Usuario.DoesNotExist:
                error = "Correo o contraseña incorrectos"
    context = {
        "form": form,
        "error": error
    }
    return render(request, 'login_administrador.html', context=context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

@administrador_required
def lista_admins(request: HttpRequest):
    admins = Administrador.objects.all()
    update_admin_form = UpdateAdministradorForm()
    registro_admin_form = AdministradorForm()
    filtros_lista_form = FiltrosListaAdminForm(request.GET)
    mostrar_modal_registro_admin = False

    if request.method == "POST":
        registro_admin_form = AdministradorForm(request.POST)
        if registro_admin_form.is_valid():
            registro_admin_form.save()  # <-- ahora hace todo internamente
            registro_admin_form = AdministradorForm()
        else:
            mostrar_modal_registro_admin = True
            messages.error(
                request, "Por favor corrige los errores del formulario.")

    busqueda: str = filtros_lista_form.data.get('busqueda_texto', '').strip()
    if len(busqueda) > 0:
        admins = admins.filter(
            Q(usuario__nombre__icontains=busqueda) |
            Q(usuario__correo__icontains=busqueda) |
            Q(programa_academico__nombre_programa__icontains=busqueda)
        )

    match filtros_lista_form.data.get('estado_cuenta', ''):
        case 'activos':
            admins = admins.filter(usuario__is_active=True)
        case 'inactivos':
            admins = admins.filter(usuario__is_active=False)
        case _:
            pass
    
    paginator = Paginator(admins, 10)
    page_number = int(request.GET.get('page', "1"))

    try:
        admins_page = paginator.page(page_number)
    except PageNotAnInteger:
        admins_page = paginator.page(1)
    except EmptyPage:
        admins_page = paginator.page(paginator.num_pages)

    context = {
        "admins": admins_page,
        "update_admin_form": update_admin_form,
        "admins_totales": admins.count(),
        "admins_activos": admins.filter(usuario__is_active=True).count(),
        "filtros_lista_form": filtros_lista_form,
        "registro_admin_form": registro_admin_form,
        "mostrarModalCrearAdmin": mostrar_modal_registro_admin
    }
    return render(request, 'lista_admins.html', context=context)

@administrador_required
def detalle_admin(request, id_admin: int):
    print(f"Id admin: {id_admin}", flush=True) 
    admin = get_object_or_404(Administrador, pk=id_admin)

    return JsonResponse(
        data={
            "id_admin": admin.id_administrador,
            "nombre": admin.usuario.nombre,
            "correo": admin.usuario.correo,
            "programa_academico": admin.programa_academico.pk,
            "estado_cuenta": admin.usuario.is_active
        }
    )

@administrador_required
def actualizar_info_admin(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse(
            status=405
        )
    
    form = UpdateAdministradorForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            data={
                "errors": form.errors
            },
            status=400
        )
    try:
        form.save()
    except forms.ValidationError as e:
        return JsonResponse(
            data={
                'errors': {
                    'non_field_errors': e.message
                }
            },
            status=400
        )
    return JsonResponse(
        data={},
        status=200
    )