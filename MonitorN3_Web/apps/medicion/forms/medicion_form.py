from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from ..models import Medicion
from ...instrumento.models import Instrumento

class MedicionPiezometroForm(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='PIEZÓMETRO', activo=True),
        label= 'Seleccionar Piezómetro',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lectura = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'})

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MedicionUpdateForm(forms.ModelForm):
    class Meta:
        model = Medicion
        fields = ['fecha', 'valor']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'fecha': 'Fecha de la medición',
            'valor': 'Valor',
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

    volumen_1 = forms.FloatField(label='Volumen [l]', required=False,
                                 widget=forms.NumberInput(
                                     attrs={'class': 'form-control', 'placeholder': 'Volumen (l)', 'step': '0.01', 'min': '0'}))
    tiempo_1 = forms.FloatField(label='Tiempo (s)', required=False,
                                widget=forms.NumberInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Tiempo (s)', 'step': '0.01', 'min': '0'}))

    volumen_2 = forms.FloatField(label='Volumen [l]', required=False,
                                 widget=forms.NumberInput(
                                     attrs={'class': 'form-control', 'placeholder': 'Volumen (l)', 'step': '0.01', 'min': '0'}))
    tiempo_2 = forms.FloatField(label='Tiempo (s)', required=False,
                                widget=forms.NumberInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Tiempo (s)', 'step': '0.01','min': '0'}))

    volumen_3 = forms.FloatField(label='Volumen [l]', required=False,
                                 widget=forms.NumberInput(
                                     attrs={'class': 'form-control', 'placeholder': 'Volumen (l)', 'step': '0.01', 'min': '0'}))
    tiempo_3 = forms.FloatField(label='Tiempo (s)', required=False,
                                widget=forms.NumberInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Tiempo (s)', 'step': '0.01', 'min': '0'}))

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        errores = []

        for campo in ['volumen_1', 'volumen_2', 'volumen_3', 'tiempo_1', 'tiempo_2', 'tiempo_3']:
            valor = cleaned_data.get(campo)

            if valor is not None:
                if valor < 0:
                    errores.append(f"{self.fields[campo].label} no puede ser negativo.")

        if errores:
            raise ValidationError(errores)

        return cleaned_data

class MedicionAforadorParshall(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='AFORADOR PARSHALL', activo=True),
        label='Seleccionar Aforador',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }