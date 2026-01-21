from django.db import models
from clientes.models import Cliente
from productos.models import Producto

class Factura(models.Model):
    FORMA_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('OTROS', 'Otros'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    numero = models.CharField(max_length=20, unique=True)  # ej: 001-001-000000123
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO, default='EFECTIVO')

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal_cero = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    clave_acceso = models.CharField(max_length=150, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    estado = models.CharField(max_length=20, default="ACTIVA")  # ACTIVA / ANULADA

    def __str__(self):
        return f"Factura {self.numero} - {self.cliente.nombre_razon_social}"

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
