from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from usuarios.models import Denunciante, Usuario

class RegistrarDenuncianteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("crear_cuenta_denunciante")

    def test_registrar_denunciante(self):
        data = {
            "correo": "nuevo@uaz.mx",
            "nombre": "Nuevo Usuario",
            "contrasena": "pass1234",
            "confirmar_contrasena": "pass1234"
        }

        resp = self.client.post(self.url, data, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Usuario.objects.filter(correo="nuevo@uaz.mx").exists())
        self.assertTrue(Denunciante.objects.filter(usuario__correo="nuevo@uaz.mx").exists())
        self.assertContains(resp, "correo")     # aparece en estado_envio_correo.html
