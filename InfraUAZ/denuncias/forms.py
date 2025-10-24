from django import forms
from .models import TipoDenuncia, ProgramaAcademico, Edificio, TipoLugarReferencia, LugarReferencia

class DenunciaForm(forms.Form):
    titulo = forms.CharField(
        max_length=100,
        label='Título de la denuncia',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",  
                "placeholder": "Ej. Silla rota"
            }
        )
    )


    descripcion = forms.CharField(
        max_length=500,
        label='Descripción del incidente',
        widget=forms.Textarea(
            attrs={
                    "class": "form-control",
                    "placeholder": "Describe el incidente en detalle..."
            }
        )
    )

    # aqui voy hacer las consultas desde el formas, en vez de las vistas
    tipo_denuncia = forms.ModelChoiceField(
        queryset=TipoDenuncia.objects.all(),
        label='Tipo de denuncia *',
        empty_label='Seleccione el tipo de denuncia',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "tipo_denuncia"
        })
    )


    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        label = 'Edificio *',
        empty_label= 'Seleccione el edificio',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "edificio"
        })
    )
    programa = forms.ModelChoiceField(
        queryset=ProgramaAcademico.objects.none(),
        label = 'Programa académico *',
        empty_label= 'Seleccione el programa académico',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "programa"
        })
    )

    tipo_lugar = forms.ModelChoiceField(
        queryset= TipoLugarReferencia.objects.all(),
        empty_label= 'Seleccione el tipo de lugar',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "tipoLugar"
        })
    )

    lugarReferencia = forms.ModelChoiceField(
        queryset=ProgramaAcademico.objects.none(),
        label = 'Programa académico *',
        empty_label= 'Seleccione el lugar de referencia',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "lugarReferencia"
        })
    )





