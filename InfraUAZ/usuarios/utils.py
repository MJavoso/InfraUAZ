from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from enum import Enum
from .models import Administrador, Denunciante, Usuario

class EmailStatus(Enum):
    EMAIL_FAILED = "email_failed"
    EMAIL_SENT = "email_sent"
    USER_ACTIVATED = "user_activated"
    USER_FAILED_ACTIVATE = "user_failed_activate"
    USER_ACTIVE = "user_active"
    USER_EXISTS = "user_exists"

def es_administrador(id_usuario: int):
    return Administrador.objects.filter(pk=id_usuario).exists()

def enviar_correo_activacion(dominio: str, correo: str, nombre: str, denunciante: Denunciante, usuario: Usuario):
    asunto = 'Activación de cuenta - InfraUAZ'
    remitente = 'infrauaz+noreply@uaz.edu.mx'
    destinatarios = [correo]
    uid = urlsafe_base64_encode(force_bytes(denunciante.id_denunciante))
    token = default_token_generator.make_token(usuario)

    endpoint_activacion = reverse('activar_cuenta', kwargs={'uidb64': uid, 'token': token})
    url_activacion = f'http://{dominio}{endpoint_activacion}'

    html_content = render_to_string(
        template_name='emails/activar_cuenta.html',
        context={
            'nombre': nombre,
            'url_activacion': url_activacion
        }
    )
    text_content = f'Hola {nombre}, activa tu cuenta de InfraUAZ en {url_activacion}'

    email = EmailMultiAlternatives(asunto, text_content, remitente, destinatarios)
    email.attach_alternative(html_content, mimetype='text/html')
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f'Error al envíar el correo: {e}')
        return False

def activar_cuenta_denunciante(uid, token) -> EmailStatus:
    try:
        uid = int(urlsafe_base64_decode(uid))
        usuario = Denunciante.objects.get(pk=uid).usuario
    except (TypeError, ValueError, Denunciante.DoesNotExist):
        usuario = None
    if usuario.is_active:
        return EmailStatus.USER_ACTIVE
    
    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        return EmailStatus.USER_ACTIVATED
    else:
        return EmailStatus.USER_FAILED_ACTIVATE