from django.db import models
from ..embalse.models import Embalse

class Precipitacion(models.Model):
    fecha = models.OneToOneField(Embalse, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tres_dias_previos = models.DecimalField(max_digits=10, decimal_places=2)
    cinco_dias_previos = models.DecimalField(max_digits=10, decimal_places=2)
    diez_dias_previos = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'precipitacion'

    def __str__(self):
        return f"Fecha: {self.fecha} - Valor: {self.valor}"
