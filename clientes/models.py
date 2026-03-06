from django.db import models
from django.conf import settings

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
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_razon_social} - {self.identificacion}"


class ClienteAccount(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name="account")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cliente_account")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    debe_cambiar_password = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.cliente.nombre_razon_social} ({self.cliente.identificacion}) -> {self.user.username}"
