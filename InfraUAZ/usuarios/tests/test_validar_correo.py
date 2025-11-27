from django.test import Client, TestCase
from django.urls import reverse
from usuarios.models import Denunciante, Usuario
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class ValidacionCorreoTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Crear usuario sin verificar
        self.user = Usuario.objects.create_user(
            correo="prueba@uaz.mx",
            nombre="Prueba",
            contrasena="pass1234",
            is_active=True 
            )
        self.denunciante = Denunciante.objects.create(usuario=self.user)
        self.user.save()

    def test_validar_correo(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)        
        url_validar = reverse("activar_cuenta", args=[uid, token])
        
        # Simular la solicitud GET para activar la cuenta
        resp = self.client.get(url_validar, follow=True) 
        self.assertEqual(resp.status_code, 200)
        # Verificar el mensaje de éxito que muestra la vista
        self.assertContains(resp, 'Tu cuenta fue activada.') 
        # Refrescar el objeto en memoria para ver el cambio en la BD
        self.user.refresh_from_db()
        # El usuario ya debe estar activado
        self.assertTrue(self.user.verificado)