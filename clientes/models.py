from django.db import models

class Cliente(models.Model):
    TIPO_IDENTIFICACION = [
        ('CED', 'Cédula'),
        ('RUC', 'RUC'),
        ('PAS', 'Pasaporte'),
    ]

    tipo_identificacion = models.CharField(max_length=3, choices=TIPO_IDENTIFICACION)
    identificacion = models.CharField(max_length=20, unique=True)
    nombre_razon_social = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    estado = models.BooleanField(default=True)  # cliente activo/inactivo

    def __str__(self):
        return f"{self.nombre_razon_social} - {self.identificacion}"
