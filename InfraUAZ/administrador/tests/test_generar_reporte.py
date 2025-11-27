from django.urls import reverse
from usuarios.models import Usuario
from django.test import Client, TestCase


class ReportePDFTests(TestCase):

    def setUp(self):
        self.client = Client()
        admin = Usuario.objects.create_user(
            correo="adminpdf@uaz.mx",
            nombre="Admin",
            contrasena="pass"
        )
        admin.is_staff = True
        admin.is_active = True
        admin.verificado = True
        admin.save()

        self.client.force_login(admin)

    def test_generar_reporte(self):
        url = reverse("reporte_denuncias_pdf")  
        resp = self.client.post(url, {"estado": 1})

        self.assertIn(resp.status_code, (200, 302))
