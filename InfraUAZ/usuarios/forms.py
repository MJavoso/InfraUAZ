from django import forms
from .validators import validar_correo_uaz
from .models import Denunciante, Usuario

class DenuncianteForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre completo',
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Ej. Juan Pérez García"
            }
        )
    )
    correo = forms.EmailField(
        label='Correo institucional',
        validators=[validar_correo_uaz],
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": 'correo@uaz.edu.mx'
            }
        )
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": 'Mínimo 8 caracteres'
            }
        ),
        label='Contraseña', min_length=8
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": 'Repite tu contraseña'
            }
        ),
        label='Confirmar contraseña',
        min_length=8,
    )
    
    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if len(contrasena) < 8:
            raise forms.ValidationError('La contraseña debe de ser mínimo de 8 caracteres')
        
        if contrasena != confirmar_contrasena:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return cleaned_data
    
    def save(self):
        nombre = self.cleaned_data['nombre']
        correo = self.cleaned_data['correo']
        contrasena = self.cleaned_data['contrasena']
        
        if Usuario.objects.filter(correo=correo).first() is not None:
            raise forms.ValidationError('El usuario ya existe')

        usuario = Usuario.objects.create_user(correo=correo, nombre=nombre, contrasena=contrasena)
        denunciante = Denunciante.objects.create(usuario=usuario)
        return denunciante