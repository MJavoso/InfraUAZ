from django.urls import reverse
from usuarios.models import Usuario
from django.test import Client, TestCase


class RegistrarAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            correo="joaquin@uaz.mx", 
            nombre="Joaquin", 
            contrasena="pass"
        )
        self.admin.is_staff = True
        self.admin.verificado = True
        self.admin.is_active = True
        self.admin.save()

        self.client.force_login(self.admin)

    def test_registrar_admin(self):
        url = reverse("lista_admins")
        data = {
            "correo": "nuevoadmin@uaz.mx",
            "nombre": "Nuevo Admin",
            "contrasena": "pass1234",
            "confirmar_contrasena": "pass1234",
            "programa_academico": 1
        }

        resp = self.client.post(url, data, follow=True)
        self.assertIn(resp.status_code, (200, 302))
