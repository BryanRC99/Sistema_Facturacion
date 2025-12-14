from django.db import models

class Proveedor(models.Model):

    TIPO_IDENTIFICACION = [
        ('RUC', 'RUC'),
        ('CEDULA', 'Cédula'),
        ('PASAPORTE', 'Pasaporte'),
    ]

    tipo_identificacion = models.CharField(
        max_length=15,
        choices=TIPO_IDENTIFICACION
    )

    identificacion = models.CharField(
        max_length=20,
        unique=True
    )

    nombre_razon_social = models.CharField(
        max_length=150
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    celular = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=255
    )

    correo = models.EmailField(
        blank=True,
        null=True
    )

    contacto_nombre = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    contacto_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    estado = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_razon_social
