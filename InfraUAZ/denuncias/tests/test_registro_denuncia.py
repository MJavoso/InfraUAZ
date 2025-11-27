from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from usuarios.models import Usuario, Denunciante
from denuncias.models import (
Denuncia, TipoDenuncia, LugarReferencia,
ProgramaAcademico, EstadoDenuncia
)

class TestReporteDenuncia(TestCase):

    # Fixtures de valores ya precargados en la base de datos
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
    # Crear usuario y denunciante
        self.user = Usuario.objects.create_user(
            correo="denunc@uaz.mx",
            nombre="Juan Pérez",
            contrasena="pass1234"
        )
        # Otorgar permisos a los usuarios 
        self.user.is_active = True 
        self.user.verificado = True 
        self.user.save()
        #Creamos el usuario
        self.denunciante = Denunciante.objects.create(usuario=self.user)

    # Cargar los datos reales desde los fixtures
        self.programa = ProgramaAcademico.objects.first()
        self.lugar = LugarReferencia.objects.first()
        self.tipo_denuncia = TipoDenuncia.objects.first()
        self.estado = EstadoDenuncia.objects.get(estado="PENDIENTE")

    # Iniciar sesión
        self.user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.client.force_login(self.user)

    # Test de crear un post de denuncia
    def test_crear_denuncia_post(self):
        url = reverse("crear_denuncia")

        data = {
            "titulo": "Fuga de agua en el baño",
            "descripcion": "Se está tirando el agua en el piso",
            "tipo_denuncia": self.tipo_denuncia.id_tipo_denuncia,
            "lugarReferencia": self.lugar.id_lugar,
            "programa": self.programa.id_programa,
            "edificio": self.programa.id_edificio.id_edificio,
            "tipo_lugar": self.lugar.id_tipo.id_tipo
        }
        # Redireccionar a la url y pasar los datos por post
        resp = self.client.post(url, data, follow=True) 
        self.assertEqual(resp.status_code, 200, 
                     f"El POST falló. Status code: {resp.status_code}.")
        # Intenta buscar usando 'título' - basado en forms.py
        try:
            self.assertTrue(
                Denuncia.objects.filter(
                    título__icontains="Fuga de agua"
                ).exists(),
                "La denuncia no se guardó"
            )
        # Si falla por tilde, intenta sin tilde
        except:
            self.assertTrue(
                Denuncia.objects.filter(
                    titulo__icontains="Fuga de agua"
                ).exists(),
                "La denuncia no se guardó. La validación del formulario falló."
            ) 

# TC-04: Ver denuncias del denunciante
    def test_ver_mis_denuncias(self):
        # Creamos una denuncia
        Denuncia.objects.create(
            título="Denuncia Test",
            descripcion="Esto se debe guardar JAJAJA",
            id_denunciante=self.denunciante,
            id_tipo_denuncia=self.tipo_denuncia,
            id_lugar=self.lugar,
            id_estado=self.estado,
            fecha=timezone.now().date()
        )
        # Guardamos y redirigimos a la URL
        url = reverse("perfil")
        resp = self.client.get(url)

    # Debe cargar bien la vista
        self.assertEqual(resp.status_code, 200)

    # Y debe mostrar la denuncia creada
        self.assertContains(resp, "Denuncia Test")
