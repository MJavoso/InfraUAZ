from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from denuncias.models import Denuncia, EstadoDenuncia, Insumo, TipoDenuncia, LugarReferencia, ProgramaAcademico, Edificio
from usuarios.models import Denunciante

class InsumosTests(TestCase):
    #  Cargamos los fixtures
    fixtures = [
    "edificios.yaml",
    "estadosDenuncia.yaml",
    "lugaresReferencia.yaml",
    "programasAcademicos.yaml",
    "tiposDenuncia.yaml",
    "tiposLugarReferencia.yaml"
    ]
    # Configuración inicial
    def setUp(self):
        self.client = Client()
        #Creamos al admin
        self.admin = Usuario.objects.create_user(
            correo='admin@edu.uaz.mx', 
            nombre='Admin Test',           
            contrasena='adminpass',                      
            )
        # Permisos especiales
        self.admin.is_staff = True
        self.admin.verificado =True
        self.admin.is_active = True
        self.admin.save()
        # Creamos al denunciante
        self.denunc_user = Usuario.objects.create_user(
            correo='d@edu.uaz.mx',
            nombre='Juancho',
            contrasena='pass'
        )
        # Permisos especiales
        self.denunc_user.is_active = True
        self.denunc_user.verificado = True
        self.denunciante = Denunciante.objects.create(usuario=self.denunc_user)
        # Valores del form de la denuncia
        self.programa = ProgramaAcademico.objects.first()
        self.lugar = LugarReferencia.objects.first()
        self.tipo_denuncia = TipoDenuncia.objects.first()
        self.estado = EstadoDenuncia.objects.get(estado="RESUELTA")
        # Creamos la denuncia a la que será agregada el insumo
        self.denuncia = Denuncia.objects.create(
            título="Algo ocupa cinta",
            descripcion="Esto se debe guardar JAJAJA",
            id_denunciante=self.denunciante,
            id_tipo_denuncia=self.tipo_denuncia,
            id_lugar=self.lugar,
            id_estado=self.estado,
            fecha=timezone.now().date()
        )

    def test_agregar_insumo_admin(self):
        # Logueo forzado
        self.client.force_login(self.admin)
        url = reverse('agregar_insumo', args=[self.denuncia.id_denuncia])
        datos_insumo = {'nombre': 'Cinta', 'cantidad': 2, 'costo': '12.50'}
        respuesta = self.client.post(url, datos_insumo, follow=True)
        self.assertIn(respuesta.status_code, (200, 302))
        #Existe el insumo
        self.assertTrue(Insumo.objects.filter(nombre='Cinta', id_denuncia=self.denuncia).exists())
        insumo = Insumo.objects.get(nombre='Cinta', id_denuncia=self.denuncia)
        self.assertEqual(insumo.cantidad, 2)
