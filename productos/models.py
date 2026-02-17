from django.db import models, transaction, IntegrityError
from categorias.models import Categoria
from proveedores.models import Proveedor
from cloudinary.models import CloudinaryField
import re


class Producto(models.Model):
    # 👇 cambiado: editable=False y blank=True para que Django no lo pida en forms
    codigo = models.CharField(max_length=20, unique=True, editable=False, blank=True)

    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    iva = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    imagen = CloudinaryField(
        'imagen',
        folder='Proyecto_Facturacion/productos',
        blank=True,
        null=True
    )

    COD_PREFIX = "PROD"
    COD_WIDTH = 5  # PROD00001

    @classmethod
    def _next_codigo(cls) -> str:
        """
        Devuelve el menor código disponible (reutiliza huecos):
        Si existen PROD00001, PROD00002, PROD00004 -> devuelve PROD00003
        """
        codes = cls.objects.filter(codigo__startswith=cls.COD_PREFIX).values_list("codigo", flat=True)

        used = set()
        for c in codes:
            m = re.search(r"(\d+)$", c or "")
            if m:
                used.add(int(m.group(1)))

        n = 1
        while n in used:
            n += 1

        return f"{cls.COD_PREFIX}{n:0{cls.COD_WIDTH}d}"

    def save(self, *args, **kwargs):
        # Solo se genera si está vacío (crear)
        if not self.codigo:
            # Reintentos por concurrencia (dos creando al mismo tiempo)
            for _ in range(10):
                self.codigo = self.__class__._next_codigo()
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    self.codigo = ""
            raise
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

