from django import forms
from django.forms import ModelForm
from ..models import Medicion
from ...instrumento.models import Instrumento

class MedicionPiezometroForm(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='PIEZÓMETRO', activo=True),
        label= 'Seleccionar Piezómetro',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lectura = forms.NumberInput(attrs={'class': 'form-control'})

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MedicionFreatimetroForm(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='FREATÍMETRO', activo=True),
        label='Seleccionar Freatímetro',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MedicionAforadorVolumetrico(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='AFORADOR VOLUMÉTRICO', activo=True),
        label='Seleccionar Aforador',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    volumen_1 = forms.FloatField(label='Volumen [l]',
                                 widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    tiempo_1 = forms.FloatField(
        label='Tiempo (s)',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01'}))

    volumen_2 = forms.FloatField(
        label='Volumen [l]',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01'}))
    tiempo_2 = forms.FloatField(
        label='Tiempo (s)',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01'}))

    volumen_3 = forms.FloatField(
        label='Volumen [l]',
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'step': '0.01'}))
    tiempo_3 = forms.FloatField(label='Tiempo (s)',
                                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MedicionAforadorParshall(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='AFORADOR PARSHALL', activo=True),
        label='Seleccionar Aforador',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha', 'valor']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }