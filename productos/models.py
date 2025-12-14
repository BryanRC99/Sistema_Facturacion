from django.db import models
from categorias.models import Categoria
from proveedores.models import Proveedor  # Importa el modelo Proveedor

class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Margen de ganancia
    stock = models.IntegerField(default=0)
    iva = models.BooleanField(default=True)  # Si aplica IVA 12%
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
