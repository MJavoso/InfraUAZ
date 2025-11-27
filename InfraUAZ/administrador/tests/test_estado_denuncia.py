from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from denuncias.models import ProgramaAcademico, Edificio, LugarReferencia, TipoDenuncia, EstadoDenuncia, Denuncia
from usuarios.models import Denunciante, Usuario

class CambiarEstadoTests(TestCase):
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

        # ADMIN
        self.admin = Usuario.objects.create_user(
            correo="admin@uaz.mx",
            nombre="Admin",
            contrasena="pass"
        )
        self.admin.is_staff = True
        self.admin.verificado = True
        self.admin.is_active = True
        self.admin.save()

        # DENUNCIANTE
        user_d = Usuario.objects.create_user(
            correo="denunciante@uaz.mx",
            nombre="Denunciante",
            contrasena="pass"
        )
        user_d.is_active = True
        user_d.verificado = True
        user_d.save()
        denunciante = Denunciante.objects.create(usuario=user_d)

        self.programa = ProgramaAcademico.objects.first()
        self.lugar = LugarReferencia.objects.first()
        self.tipo = TipoDenuncia.objects.first()
        self.estado_p = EstadoDenuncia.objects.get(estado="PENDIENTE")
        self.estado_nuevo = EstadoDenuncia.objects.get(estado="EN_PROCESO")

        self.denuncia = Denuncia.objects.create(
            título="Cambiar estado",
            descripcion="Test estado",
            id_denunciante=denunciante,
            id_tipo_denuncia=self.tipo,
            id_lugar=self.lugar,
            id_estado=self.estado_p,
            fecha=timezone.now().date()
        )

    def test_admin_cambia_estado(self):
        self.client.force_login(self.admin)

        url = reverse("cambiar_estado_denuncia", args=[self.denuncia.id_denuncia])

        resp = self.client.post(url, {
            "nuevo_estado": self.estado_nuevo.id_estado
        })

        self.assertIn(resp.status_code, (200, 302))

        self.denuncia.refresh_from_db()

        self.assertEqual(self.denuncia.id_estado, self.estado_nuevo)

