from django.db import models

class Usuario(models.Model):
    usuario = models.CharField(max_length=50, unique=True, null=False)
    contraseña = models.CharField(max_length=255, null=False)
    rol = models.CharField(max_length=50, default='admin')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.usuario