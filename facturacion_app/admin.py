from django.contrib import admin
from .models import Factura, DetalleFactura

class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    extra = 1

class FacturaAdmin(admin.ModelAdmin):
    inlines = [DetalleFacturaInline]
    list_display = ('numero', 'cliente', 'fecha', 'total', 'estado')
    search_fields = ('numero', 'cliente__nombre_razon_social')

admin.site.register(Factura, FacturaAdmin)
