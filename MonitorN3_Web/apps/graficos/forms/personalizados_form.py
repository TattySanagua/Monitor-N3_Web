from django import forms
from ...instrumento.models import Instrumento
from django_select2.forms import Select2MultipleWidget

class PersonalizadoForm(forms.Form):
    TIPO_GRAFICO_CHOICES = [
        ('line', 'Linea'),
        ('scatter', 'Puntos'),
        ('bar', 'Barras'),
    ]

    tipo_grafico = forms.ChoiceField(
        choices=TIPO_GRAFICO_CHOICES,
        label="Tipo de Gráfico (Eje Y)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='line'
    )

    tipo_grafico_y2 = forms.ChoiceField(
        choices=TIPO_GRAFICO_CHOICES,
        label="Tipo de Gráfico (Eje Y2)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='line',
        required=False
    )

    EJE_CHOICES = [
        ('fecha', 'Fecha'),
        ('nivel_embalse', 'Nivel de Embalse'),
        ('nivel_piezometrico', 'Nivel Piezométrico'),
        ('nivel_freatico', 'Nivel Freático'),
        ('caudal', 'Caudal'),
    ]

    eje_x = forms.ChoiceField(
        choices=EJE_CHOICES,
        label="Datos del eje X",
        initial='fecha',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    instrumento_x = forms.ModelMultipleChoiceField(
        queryset=Instrumento.objects.none(),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False,
        label="Instrumentos (Eje X)"
    )

    EJE_Y_CHOICES = [
        ('nivel_embalse', 'Nivel de Embalse'),
        ('nivel_piezometrico', 'Nivel Piezométrico'),
        ('nivel_freatico', 'Nivel Freático'),
        ('caudal', 'Caudal'),
        ('precipitacion', 'Precipitacion'),
    ]

    eje_y = forms.ChoiceField(
        choices=EJE_Y_CHOICES,
        label="Datos del eje Y",
        initial='nivel_embalse',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    instrumento_y = forms.ModelMultipleChoiceField(
        queryset=Instrumento.objects.none(),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False,
        label="Instrumentos (Eje Y)"
    )

    agregar_eje_y_secundario = forms.BooleanField(
        required=False,
        label="Agregar eje Y Secundario",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    eje_y_secundario = forms.ChoiceField(
        choices=EJE_Y_CHOICES,
        required=False,
        label="Datos del eje Y secundario",
        initial='nivel_embalse',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    instrumento_y2 = forms.ModelMultipleChoiceField(
        queryset=Instrumento.objects.none(),
        widget=Select2MultipleWidget(attrs={'class': 'form-control'}),
        required=False,
        label="Instrumentos (Eje Y Secundario)"
    )

    def __init__(self, *args, **kwargs):
        super(PersonalizadoForm, self).__init__(*args, **kwargs)

        #Cargar todos los instrumentos disponibles
        self.fields['instrumento_x'].queryset = Instrumento.objects.all()
        self.fields['instrumento_y'].queryset = Instrumento.objects.all()
        self.fields['instrumento_y2'].queryset = Instrumento.objects.all()

        #Filtrar instrumentos según el tipo de medición seleccionado en el eje X
        if 'eje_x' in self.data:
            eje_x_value = self.data['eje_x']
            self.fields['instrumento_x'].queryset = self.filtrar_instrumentos(eje_x_value)

        #Filtrar instrumentos según el tipo de medición seleccionado en el eje Y
        if 'eje_y' in self.data:
            eje_y_value = self.data['eje_y']
            self.fields['instrumento_y'].queryset = self.filtrar_instrumentos(eje_y_value)

        #Filtrar instrumentos según el tipo de medición seleccionado en el eje Y secundario
        if 'eje_y_secundario' in self.data:
            eje_y_secundario_value = self.data['eje_y_secundario']
            self.fields['instrumento_y2'].queryset = self.filtrar_instrumentos(eje_y_secundario_value)

    def filtrar_instrumentos(self, tipo_medicion):

        if tipo_medicion == "nivel_piezometrico":
            return Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")
        elif tipo_medicion == "nivel_freatico":
            return Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")
        elif tipo_medicion == "caudal":
            return Instrumento.objects.filter(id_tipo__nombre_tipo__in=["AFORADOR VOLUMÉTRICO", "AFORADOR PARSHALL"])
        return Instrumento.objects.none()