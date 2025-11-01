from django.core.exceptions import ValidationError
from os import getenv
from InfraUAZ.utils import str_to_bool

DOMINIO_CORREO = 'uaz.edu.mx'

_DISABLE_UAZ_EMAILS = str_to_bool(getenv('DISABLE_UAZ_EMAILS'))

def validar_correo_uaz(correo: str):
    if _DISABLE_UAZ_EMAILS:
        return
    
    if not correo.endswith(DOMINIO_CORREO):
        raise ValidationError(f'El correo debe pertenecer al dominio "{DOMINIO_CORREO}"') 