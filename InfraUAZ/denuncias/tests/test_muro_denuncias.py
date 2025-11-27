from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from denuncias.models import ProgramaAcademico, Edificio, LugarReferencia, TipoDenuncia, EstadoDenuncia, Denuncia
from usuarios.models import Denunciante, Usuario


class MuroDenunciasTests(TestCase):
    fixtures = [
        "edificios.yaml",
        "estadosDenuncia.yaml",
        "lugaresReferencia.yaml",
        "programasAcademicos.yaml",
        "tiposDenuncia.yaml",
        "tiposLugarReferencia.yaml"
    ]

    def setUp(self):
        self.client = Client()

        # Crear usuario denunciante
        self.user = Usuario.objects.create_user(
            correo="user@uaz.mx",
            nombre="Usuario",
            contrasena="pass1234"
        )
        self.user.is_active = True
        self.user.verificado = True
        self.user.save()

        self.denunciante = Denunciante.objects.create(usuario=self.user)

        # Cargar datos
        self.programa = ProgramaAcademico.objects.first()
        self.lugar = LugarReferencia.objects.first()
        self.tipo = TipoDenuncia.objects.first()
        self.estado = EstadoDenuncia.objects.get(estado="PENDIENTE")

        # Crear denuncia
        self.denuncia = Denuncia.objects.create(
            título="Denuncia Muro",
            descripcion="Prueba del muro",
            id_denunciante=self.denunciante,
            id_tipo_denuncia=self.tipo,
            id_lugar=self.lugar,
            id_estado=self.estado,
            fecha=timezone.now().date()
        )

        self.client.force_login(self.user)

    def test_muro_denuncias_carga_correctamente(self):
        url = reverse("muro_denuncias")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Denuncia Muro")

    def test_filtrar_muro_por_tipo(self):
        url = reverse("muro_denuncias")

        resp = self.client.post(url, {
            "tipo_denuncia": self.tipo.id_tipo_denuncia
        })

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Denuncia Muro")
        
    def test_filtrar_muro_por_estado(self):
        url = reverse("muro_denuncias")

        resp = self.client.post(url, {
            "estado": self.estado.id_estado
        })

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Denuncia Muro")

