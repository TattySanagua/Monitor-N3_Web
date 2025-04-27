from django.forms import ModelForm
from django import forms
from ..models import Precipitacion

class PrecipitacionForm(ModelForm):
    class Meta:
        model = Precipitacion
        fields = ['fecha', 'valor']

        labels = {
            'fecha': 'Fecha',
            'valor': 'Valor (mm)',
        }

        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }