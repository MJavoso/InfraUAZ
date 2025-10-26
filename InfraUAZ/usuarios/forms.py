from django import forms
from .validators import validar_correo_uaz
from .models import Denunciante, Usuario, Administrador
from django.core.exceptions import ValidationError

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
            self.add_error('contrasena', 'La contraseña debe ser de al menos 8 caracteres')
            return cleaned_data
        
        if contrasena != confirmar_contrasena:
            self.add_error('confirmar_contrasena', 'Las contraseñas no coinciden')
            return cleaned_data

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

class LoginForm(forms.Form):
    correo = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control bg-light",
                "placeholder": "usuario@uaz.edu.mx"
            }
        ),
        label="Correo electrónico",
        validators=[validar_correo_uaz]
    )

    contrasena = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control bg-light",
                "placeholder": "••••••••"
            }
        )
    )

    recordarme = forms.BooleanField(
        label='Recordarme',
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input"
            }
        )
    )
    

#agregar administrador
class AdministradorForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: Juan Pérez García"
        })
    )
    correo = forms.EmailField(
        label='Correo institucional',
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "correo@uaz.edu.mx"
        })
    )
    contrasena = forms.CharField(
        label='Contraseña',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Mínimo 6 caracteres"
        })
    )
    confirmar_contrasena = forms.CharField(
        label='Confirmar contraseña',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repite la contraseña"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        confirmar = cleaned_data.get('confirmar_contrasena')

        if contrasena != confirmar:
            raise ValidationError("Las contraseñas no coinciden")

        # Verificar que el correo no exista ya
        correo = cleaned_data.get('correo')
        if Administrador.objects.filter(correo=correo).exists():
            raise ValidationError("El correo ya está registrado")

        return cleaned_data

    def save(self):
        nombre = self.cleaned_data['nombre']
        correo = self.cleaned_data['correo']
        contrasena = self.cleaned_data['contrasena']

        # Crear el administrador
        admin = Administrador.objects.create(
            nombre=nombre,
            correo=correo,
            contraseña=contrasena  # Opcional: aquí podrías hashearla
        )
        return admin
