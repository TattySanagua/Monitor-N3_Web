from django.db import models
from django.utils.timezone import now

class Unidad(models.Model):
    nombre_unidad = models.CharField(max_length=50, null=False)
    simbolo = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'unidad'

    def __str__(self):
        return f"{self.nombre_unidad} ({self.simbolo})"


class Tipo(models.Model):
    id_unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE)
    nombre_tipo = models.CharField(max_length=50, null=False)
    tipo_medicion = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'tipo'

    def __str__(self):
        return self.nombre_tipo

class Instrumento(models.Model):
    nombre = models.CharField(max_length=50, null=False)
    id_tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, null=False)
    fecha_alta = models.DateField(null=True, blank=True, default=now)
    fecha_baja = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'instrumento'

    def __str__(self):
        return self.nombre

class Parametro(models.Model):
    id_instrumento = models.ForeignKey(Instrumento, on_delete=models.CASCADE, null=False)
    nombre_parametro = models.CharField(max_length=50, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=4, null=False)

    class Meta:
        db_table = 'parametro'

    def __str__(self):
        return f"{self.nombre_parametro} - {self.valor}"