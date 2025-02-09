from django.forms import ModelForm
from django import forms
from ..models import Instrumento, Tipo, Parametro

class InstrumentoForm(ModelForm):
    id_tipo = forms.ModelChoiceField(
        queryset=Tipo.objects.all(),
        label="Tipo de Instrumento",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'tipo-instrumento'})
    )
    class Meta:
        model = Instrumento
        fields = ['nombre', 'id_tipo', 'fecha_alta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class InstrumentoUpdateForm(ModelForm):
    """Formulario para editar solo el nombre y la fecha de instalación del instrumento"""
    class Meta:
        model = Instrumento
        fields = ['nombre', 'fecha_alta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ParametroForm(ModelForm):
    """Formulario para editar los parámetros de un instrumento"""
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'valor']
        widgets = {
            'nombre_parametro': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }