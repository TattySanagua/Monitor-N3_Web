from django.db import models

class Embalse(models.Model):
    fecha = models.DateField(null=False)
    hora = models.TimeField(null=False)
    nivel_embalse = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta:
        db_table = 'embalse'
        unique_together = ('fecha', 'hora')

    def __str__(self):
        return f"{self.fecha} {self.hora} - Nivel: {self.nivel_embalse}"