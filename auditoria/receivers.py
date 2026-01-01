from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from auditoria.utils import registrar_auditoria, obtener_cambios
from auditoria.models import AuditoriaLog

IGNORAR_APPS = ["sessions", "admin", "auth", "contenttypes", "auditoria"]
ACCIONES_PERMITIDAS = ["CREAR", "MODIFICAR", "ELIMINAR"]


def obtener_usuario(instance):
    """
    Obtiene el usuario almacenado temporalmente en la instancia,
    sino devuelve None.
    """
    return getattr(instance, "_current_user", None)


# ======================================================================
# 📌 AUDITORÍA GUARDAR (CREACIÓN / MODIFICACIÓN)
# ======================================================================
@receiver(post_save)
def auditoria_guardar(sender, instance, created, **kwargs):
    if sender._meta.app_label in IGNORAR_APPS:
        return

    usuario = getattr(instance, "_current_user", None)
    request = getattr(instance, "_current_request", None)

    accion = "CREAR" if created else "MODIFICAR"
    if accion not in ACCIONES_PERMITIDAS:
        return

    cambios_antes, cambios_despues = obtener_cambios(
        getattr(instance, "_before_state", None),
        instance
    )

    registrar_auditoria(
        usuario=usuario,
        accion=accion,
        modelo_afectado=sender.__name__,
        registro_id=instance.id,
        cambios_antes=cambios_antes,
        cambios_despues=cambios_despues,
        request=request
    )


# ======================================================================
# 🗑️ AUDITORÍA ELIMINACIÓN
# ======================================================================
@receiver(post_delete)
def auditoria_eliminar(sender, instance, **kwargs):
    if sender._meta.app_label in IGNORAR_APPS:
        return

    usuario = obtener_usuario(instance)

    registrar_auditoria(
        usuario=usuario,
        accion="ELIMINAR",
        modelo_afectado=sender.__name__,
        registro_id=instance.pk,
        cambios_antes=None,
        cambios_despues=None,
        request=getattr(instance, "_current_request", None)
    )
