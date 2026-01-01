import json
from django.forms.models import model_to_dict
from auditoria.models import AuditoriaLog


# ---------------------------------------------------
# 📝 Convierte modelo a dict seguro evitando errores
# ---------------------------------------------------
def modelo_a_dict_seguro(instance):
    """
    Convierte un objeto modelo en diccionario serializable
    evitando valores no JSON (FK se representan como ID).
    """

    if instance is None:
        return None

    data = model_to_dict(instance)

    # Convertimos posibles valores no serializables
    for k, v in data.items():
        try:
            json.dumps(v)
        except TypeError:
            data[k] = str(v)

    return data


# ---------------------------------------------------
# 🔍 Compara cambios entre dos instancias modelo
# ---------------------------------------------------
def obtener_cambios(instance_before, instance_after):
    """
    Devuelve solo los campos modificados entre 2 instancias
    """
    before = modelo_a_dict_seguro(instance_before)
    after = modelo_a_dict_seguro(instance_after)

    if not before or not after:
        return None, None

    cambios_antes = {}
    cambios_despues = {}

    for campo, valor_before in before.items():
        valor_after = after.get(campo)

        if valor_before != valor_after:
            cambios_antes[campo] = valor_before
            cambios_despues[campo] = valor_after

    if not cambios_antes:
        return None, None

    return cambios_antes, cambios_despues


# ---------------------------------------------------
# 📌 Registrar evento general de auditoría
# ---------------------------------------------------
def registrar_auditoria(usuario=None, accion="ACCEDER",
                        modelo_afectado="", registro_id=None,
                        cambios_antes=None, cambios_despues=None,
                        request=None):
    """
    Guarda un registro de auditoría manual o automático.

    Se puede llamar desde signals, vistas o tareas:
        registrar_auditoria(request.user, "CREAR", "Factura", factura.id, antes, despues, request)
    """

    ip = None
    user_agent = None

    # 🌐 Extraer info del request si existe
    if request:
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

    AuditoriaLog.objects.create(
        usuario=usuario,
        accion=accion,
        modelo_afectado=modelo_afectado,
        registro_id=registro_id,
        cambios_antes=cambios_antes,
        cambios_despues=cambios_despues,
        ip=ip,
        user_agent=user_agent
    )
