from django.db import models
from usuarios.models import Denunciante

class Edificio(models.Model):
    id_edificio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre
class ProgramaAcademico(models.Model):
    id_programa = models.AutoField(primary_key=True)
    nombre_programa = models.CharField(max_length=100, null=False, blank=False)
    id_edificio = models.ForeignKey(Edificio,on_delete=models.RESTRICT,null=False, blank=False)

    def __str__(self):
        return self.nombre_programa
class EstadoDenuncia(models.Model):
    id_estado = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.estado
class TipoLugarReferencia(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.nombre_tipo
class LugarReferencia(models.Model):
    id_lugar = models.AutoField(primary_key=True)
    nombre_lugar = models.CharField(max_length=100, null=False, blank=False)
    id_tipo = models.ForeignKey(TipoLugarReferencia, on_delete=models.RESTRICT, null=False, blank=False)
    id_programa =  models.ForeignKey(ProgramaAcademico, on_delete=models.RESTRICT, null=False, blank=False)
    def __str__(self):
        return self.nombre_lugar
class TipoDenuncia(models.Model):
    id_tipo_denuncia = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.descripcion
class Denuncia(models.Model):
    id_denuncia = models.AutoField(primary_key=True)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=500, null=False, blank=False)
    título = models.CharField(max_length=100, null=False, blank=False)
    id_denunciante = models.ForeignKey(Denunciante, on_delete=models.RESTRICT, null=False, blank=False)
    id_estado = models.ForeignKey(EstadoDenuncia, on_delete=models.RESTRICT, null=False, blank=False)
    id_lugar = models.ForeignKey(LugarReferencia, on_delete=models.RESTRICT, null=False, blank=False)
    id_tipo_denuncia = models.ForeignKey(TipoDenuncia, on_delete=models.RESTRICT, null=False, blank=False)
    def __str__(self):
        return self.descripcion
class FotografiaEvidencia(models.Model):
    id_foto = models.AutoField(primary_key=True)
    uriFoto = models.ImageField(upload_to='evidencias/')
    fecha_subida = models.DateField(auto_now_add=True)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.RESTRICT, null=False, blank=False)

class Insumo (models.Model):
    id_insumo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    cantidad = models.IntegerField(null=False)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    id_denuncia = models.ForeignKey(Denuncia, on_delete=models.RESTRICT, null=False, blank=False)

    def __str__(self):
        return self.nombre