from django import forms
from .validators import validar_correo_uaz
from .models import Denunciante, Usuario, Administrador
from django.core.exceptions import ValidationError
from denuncias.models import ProgramaAcademico

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
    
    def save(self) -> tuple[Usuario, Denunciante]:
        nombre = self.cleaned_data['nombre']
        correo = self.cleaned_data['correo']
        contrasena = self.cleaned_data['contrasena']
        usuario = Usuario.objects.filter(correo=correo).first()
        if usuario is not None:
            if not usuario.is_active:
                denunciante = Denunciante.objects.filter(usuario=usuario).first()
                raise forms.ValidationError(
                    message='Usuario existente. Necesita activar su cuenta',
                    code='user_exists',
                    params={
                        'denunciante_id': denunciante.id_denunciante
                    }
                )
            else:
                raise forms.ValidationError("El usuario ya existe.")

        usuario = Usuario.objects.create_user(correo=correo, nombre=nombre, contrasena=contrasena)
        denunciante = Denunciante.objects.create(usuario=usuario)
        return (usuario, denunciante)
    

#agregar administrador
class AdministradorForm(forms.Form):
    correo = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'})
    )
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma la contraseña'})
    )
    programa_academico = forms.ModelChoiceField(
        label="Programa Académico",
        queryset=ProgramaAcademico.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        #Validar que las contraseñas coincidan
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data
    
    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def save(self):
        correo = self.cleaned_data['correo']
        nombre = self.cleaned_data['nombre']
        contrasena = self.cleaned_data['contrasena']
        programa = self.cleaned_data['programa_academico']

        
        usuario = Usuario.objects.create_staff_user(
            correo=correo,
            nombre=nombre,
            contrasena=contrasena
        )

        admin = Administrador.objects.create(
            usuario=usuario,
            programa_academico=programa
        )

        return admin

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
