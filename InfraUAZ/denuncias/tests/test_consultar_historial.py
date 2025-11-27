from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from denuncias.models import Denuncia, EstadoDenuncia, Insumo, TipoDenuncia, LugarReferencia, ProgramaAcademico, Edificio
from usuarios.models import Denunciante

class ConsultarHistorialTests(TestCase):
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
        self.user = Usuario.objects.create_user(
            correo="hist@uaz.mx",
            nombre="Historial",
            contrasena="pass1"
        )
        self.user.verificado = True
        self.user.is_active = True
        self.user.save()
        self.denunciante = Denunciante.objects.create(usuario=self.user)

        self.estado = EstadoDenuncia.objects.get(estado="PENDIENTE")
        self.programa = ProgramaAcademico.objects.first()
        self.tipo = TipoDenuncia.objects.first()
        self.lugar = LugarReferencia.objects.first()

        Denuncia.objects.create(
            título="Denuncia 1",
            descripcion="Hola a todos JAJAJA",
            id_denunciante=self.denunciante,
            id_tipo_denuncia=self.tipo,
            id_lugar=self.lugar,
            id_estado=self.estado,
            fecha=timezone.now()
        )
        
        Denuncia.objects.create(
            título="Denuncia 2",
            descripcion="Hola a todos de nuevo JAJAJA",
            id_denunciante=self.denunciante,
            id_tipo_denuncia=self.tipo,
            id_lugar=self.lugar,
            id_estado=self.estado,
            fecha=timezone.now()
        )

        self.client.force_login(self.user)

    def test_consultar_historial(self):
        resp = self.client.get(reverse("perfil"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Denuncia 1")
        self.assertContains(resp, "Denuncia 2")
