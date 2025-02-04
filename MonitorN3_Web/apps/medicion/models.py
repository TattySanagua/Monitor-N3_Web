from django.db import models
from ..instrumento.models import Instrumento
from ..usuario.models import Usuario

class Medicion(models.Model):
    # id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=False) Agregar mas adelante
    id_instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=False)
    fecha = models.DateField(null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta:
        db_table = 'medicion'

    def __str__(self):
        return f"{self.id_instrumento.nombre} - {self.fecha} - {self.valor}"

