# auditoria/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from auditoria.utils import obtener_cambios, registrar_auditoria
from auditoria.middleware import get_current_request, get_current_user

# Modelos a auditar (ajusta a tus apps reales)
MONITOREAR_MODELOS = [
    "facturacion_app.Factura",
    "clientes.Cliente",
    "productos.Producto",
]

# Si quieres auditar detalles de factura, agrega:
# "facturacion_app.DetalleFactura",


def modelo_en_auditoria(instance):
    full_name = f"{instance._meta.app_label}.{instance.__class__.__name__}"
    return full_name in MONITOREAR_MODELOS


@receiver(pre_save)
def pre_guardar_auditoria(sender, instance, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    if not instance.pk:
        instance._auditoria_before = None
        return

    try:
        instance._auditoria_before = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._auditoria_before = None


@receiver(post_save)
def post_guardar_auditoria(sender, instance, created, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    request = get_current_request()
    usuario = get_current_user()

    modelo = instance.__class__.__name__

    if created:
        registrar_auditoria(
            usuario=usuario,
            accion="CREAR",
            modelo_afectado=modelo,
            registro_id=instance.pk,
            cambios_antes=None,
            cambios_despues=None,
            request=request
        )
        return

    before = getattr(instance, "_auditoria_before", None)
    antes, despues = obtener_cambios(before, instance)

    # Solo registra si hubo cambios reales
    if antes:
        registrar_auditoria(
            usuario=usuario,
            accion="EDITAR",
            modelo_afectado=modelo,
            registro_id=instance.pk,
            cambios_antes=antes,
            cambios_despues=despues,
            request=request
        )


@receiver(post_delete)
def eliminar_auditoria(sender, instance, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    request = get_current_request()
    usuario = get_current_user()

    registrar_auditoria(
        usuario=usuario,
        accion="ELIMINAR",
        modelo_afectado=instance.__class__.__name__,
        registro_id=instance.pk,
        cambios_antes=None,
        cambios_despues=None,
        request=request
    )
