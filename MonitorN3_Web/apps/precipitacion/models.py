from django.db import models

class Precipitacion(models.Model):
    fecha = models.DateField(null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'precipitacion'

    def __str__(self):
        return f"Fecha: {self.fecha} - Valor: {self.valor}"
