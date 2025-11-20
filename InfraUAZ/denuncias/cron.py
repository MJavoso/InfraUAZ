from django.utils import timezone
from .models import FotografiaEvidencia
import datetime
from django.db import transaction


from django.utils import timezone
from .models import FotografiaEvidencia
from django.db import transaction



DAYS = 7
def borrar_fotos():
    fotos = FotografiaEvidencia.objects.all()
    
    for foto in fotos:
        # Asegurarse de que la fecha sea aware
        fecha_subida = foto.fecha_subida
        if timezone.is_naive(fecha_subida):
            fecha_subida = timezone.make_aware(fecha_subida)
        
        fecha_restante = timezone.now() - fecha_subida

        if fecha_restante.days > DAYS:
            try:
                if foto.uriFoto:
                    foto.uriFoto.delete(save=False)  # borra archivo físico
                with transaction.atomic():
                    foto.delete()  # borra registro
                print(f"Eliminada foto -> id={foto.id_foto}")
            except Exception as e:
                print(f"Error eliminando foto id={foto.id_foto}: {e}")


# Para pruebas por minuto
# MINUTES = 1


# def borrar_fotos():
#     fotos = FotografiaEvidencia.objects.all()
    
#     for foto in fotos:
#         # Asegurarse de que la fecha sea aware
#         fecha_subida = foto.fecha_subida
#         if timezone.is_naive(fecha_subida):
#             fecha_subida = timezone.make_aware(fecha_subida)
        
#         fecha_restante = timezone.now() - fecha_subida

#         # Comparación en segundos para MINUTES
#         if fecha_restante.total_seconds() >= MINUTES * 60:
#             try:
#                 if foto.uriFoto:
#                     foto.uriFoto.delete(save=False)  # borra archivo físico
#                 with transaction.atomic():
#                     foto.delete()  # borra registro
#                 print(f"Eliminada foto -> id={foto.id_foto}")
#             except Exception as e:
#                 print(f"Error eliminando foto id={foto.id_foto}: {e}")