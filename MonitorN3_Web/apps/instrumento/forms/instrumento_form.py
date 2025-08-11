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
            'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
        }

class InstrumentoUpdateForm(ModelForm):
    class Meta:
        model = Instrumento
        fields = ['nombre', 'fecha_alta']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_alta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1997-01-01'}),
        }

class ParametroForm(ModelForm):
    class Meta:
        model = Parametro
        fields = ['nombre_parametro', 'valor']
        widgets = {
            'nombre_parametro': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nombre_parametro'].disabled = True

        nombre = self.initial.get('nombre_parametro', '').lower()
        if nombre in ['ci', 'angulo']:
            self.fields['valor'].disabled = True