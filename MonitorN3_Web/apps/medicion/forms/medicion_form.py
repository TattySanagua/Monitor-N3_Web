from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from ..models import Medicion
from ...instrumento.models import Instrumento
from datetime import date

class MedicionPiezometroForm(ModelForm):
    id_instrumento = forms.ModelChoiceField(
        queryset=Instrumento.objects.filter(id_tipo__nombre_tipo='PIEZÓMETRO', activo=True),
        label= 'Seleccionar Piezómetro',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lectura = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'})

    class Meta:
        model = Medicion
        fields = ['id_instrumento', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
        }

class MedicionUpdateForm(forms.ModelForm):
    class Meta:
        model = Medicion
        fields = ['fecha', 'valor']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'fecha': 'Fecha de la medición',
            'valor': 'Valor (msnm)',
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
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
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
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mensajes personalizados de error por campo
        self.fields['id_instrumento'].error_messages['required'] = 'Debe seleccionar un aforador.'

        for nombre_campo in ['volumen_1', 'volumen_2', 'volumen_3', 'tiempo_1', 'tiempo_2', 'tiempo_3']:
            self.fields[nombre_campo].error_messages['required'] = 'Este campo es obligatorio.'

    def clean(self):
        cleaned_data = super().clean()
        instrumento = cleaned_data.get('id_instrumento')
        fecha = cleaned_data.get('fecha')

        if fecha and fecha < date(1997, 1, 1):
            self.add_error('fecha', "La fecha debe ser posterior al 1 de enero de 1997.")

        if instrumento and fecha:
            existe = Medicion.objects.filter(id_instrumento=instrumento, fecha=fecha).exists()
            if existe:
                self.add_error(None,
                               "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada.")

        for campo in ['volumen_1', 'volumen_2', 'volumen_3', 'tiempo_1', 'tiempo_2', 'tiempo_3']:
            valor = cleaned_data.get(campo)

            if valor is not None and valor < 0:
                self.add_error(campo, f"{self.fields[campo].label} no puede ser negativo.")

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
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
        }