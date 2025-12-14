from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_razon_social',
        'tipo_identificacion',
        'identificacion',
        'telefono',
        'celular',
        'correo',
        'ciudad',
        'estado',
    )

    search_fields = (
        'nombre_razon_social',
        'identificacion',
        'correo',
    )

    list_filter = (
        'estado',
        'tipo_identificacion',
        'ciudad',
    )

    ordering = ('nombre_razon_social',)

    list_editable = ('estado',)

    fieldsets = (
        ('Información del Proveedor', {
            'fields': (
                'tipo_identificacion',
                'identificacion',
                'nombre_razon_social',
                'direccion',
                'ciudad',
                'estado',
            )
        }),
        ('Contacto', {
            'fields': (
                'telefono',
                'celular',
                'correo',
            )
        }),
        ('Contacto Alterno', {
            'fields': (
                'contacto_nombre',
                'contacto_telefono',
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',)
        }),
    )

    readonly_fields = ('fecha_creacion',)
