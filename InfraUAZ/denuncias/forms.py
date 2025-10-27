from django import forms
from .models import TipoDenuncia, Denunciante,ProgramaAcademico, Edificio, TipoLugarReferencia, LugarReferencia, Denuncia, EstadoDenuncia
from django.utils import timezone

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
        queryset=LugarReferencia.objects.none(),
        label = 'Programa académico *',
        empty_label= 'Seleccione el lugar de referencia',
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "lugarReferencia"
        })
    )

    def save(self, usuario):
        print ("ENTRADO AL SAFE")
        descripcion = self.cleaned_data['descripcion']
        título = self.cleaned_data['titulo']
        id_lugar = self.cleaned_data['lugarReferencia']
        id_tipo_denuncia = self.cleaned_data['tipo_denuncia']

        # crear la denuncia
        denuncia = Denuncia.objects.create(
            fecha = timezone.now().date(),
            título = título,
            id_estado = EstadoDenuncia.objects.get(estado = 'EN_PROCESO'),
            descripcion=descripcion,
            id_denunciante = Denunciante.objects.get(usuario=usuario),
            id_lugar = id_lugar,
            id_tipo_denuncia = id_tipo_denuncia
        )
        return denuncia



