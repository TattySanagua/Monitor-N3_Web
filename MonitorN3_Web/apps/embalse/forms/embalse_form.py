from django.forms import ModelForm
from django import forms
from ..models import Embalse

class EmbalseForm(ModelForm):
    class Meta:
        model = Embalse
        fields='__all__'

        labels = {
            'fecha': 'Fecha',
            'hora': 'Hora',
            'nivel_embalse': 'Nivel Embalse (msnm)',
        }

        widgets={
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nivel_embalse':forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }