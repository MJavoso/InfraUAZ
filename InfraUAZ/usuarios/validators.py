from django.core.exceptions import ValidationError

DOMINIO_CORREO = 'uaz.edu.mx'

def validar_correo_uaz(correo: str):
    if not correo.endswith(DOMINIO_CORREO):
        raise ValidationError(f'El correo debe pertenecer al dominio "{DOMINIO_CORREO}"')