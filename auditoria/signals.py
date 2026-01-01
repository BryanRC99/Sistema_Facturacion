from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from auditoria.utils import obtener_cambios, registrar_auditoria


# ---------------------------------------------------
# 📌 Modelos que queremos auditar
# agrega más si deseas
# ---------------------------------------------------
MONITOREAR_MODELOS = [
    "facturacion_app.Factura",
    "clientes.Cliente",
    "productos.Producto",
]


def modelo_en_auditoria(instance):
    """
    Verifica si el modelo está en la lista de auditoría
    """
    full_name = f"{instance._meta.app_label}.{instance.__class__.__name__}"
    return full_name in MONITOREAR_MODELOS


# ---------------------------------------------------
# 📝 Guardar estado anterior antes de actualizar
# ---------------------------------------------------
@receiver(pre_save)
def pre_guardar_auditoria(sender, instance, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    if not instance.pk:
        # es una creación
        instance._auditoria_before = None
        return

    try:
        antes = sender.objects.get(pk=instance.pk)
        instance._auditoria_before = antes
    except sender.DoesNotExist:
        instance._auditoria_before = None


# ---------------------------------------------------
# 💾 Registrar auditoría después de guardar
# ---------------------------------------------------
@receiver(post_save)
def post_guardar_auditoria(sender, instance, created, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    usuario = getattr(instance, "_auditoria_user", None)
    before = getattr(instance, "_auditoria_before", None)

    if created:
        # Registro nuevo
        registrar_auditoria(
            usuario=usuario,
            accion="CREAR",
            modelo_afectado=instance.__class__.__name__,
            registro_id=instance.pk
        )
    else:
        # Comparar cambios
        antes, despues = obtener_cambios(before, instance)
        if antes:
            registrar_auditoria(
                usuario=usuario,
                accion="EDITAR",
                modelo_afectado=instance.__class__.__name__,
                registro_id=instance.pk,
                cambios_antes=antes,
                cambios_despues=despues
            )


# ---------------------------------------------------
# ❌ Registrar eliminación
# ---------------------------------------------------
@receiver(post_delete)
def eliminar_auditoria(sender, instance, **kwargs):
    if not modelo_en_auditoria(instance):
        return

    usuario = getattr(instance, "_auditoria_user", None)

    registrar_auditoria(
        usuario=usuario,
        accion="ELIMINAR",
        modelo_afectado=instance.__class__.__name__,
        registro_id=instance.pk,
    )
