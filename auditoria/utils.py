# auditoria/utils.py
import json
from django.forms.models import model_to_dict
from auditoria.models import AuditoriaLog

# Campos típicos que no aportan valor en auditoría
IGNORAR_CAMPOS_DEFAULT = {
    "updated_at", "modified_at", "fecha_modificacion",
    "last_login", "password"
}


def get_client_ip(request):
    """
    Obtiene IP real de forma consistente.
    - Local: REMOTE_ADDR
    - Proxy: X-Forwarded-For (primer IP)
    - Cloudflare: CF-Connecting-IP
    """
    if not request:
        return None

    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return cf_ip.strip()

    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    if not request:
        return None
    return request.META.get("HTTP_USER_AGENT", None)


def modelo_a_dict_seguro(instance, ignorar_campos=None):
    """
    Convierte un modelo a dict serializable.
    - FK se representa como su ID en model_to_dict
    - Valores no serializables se convierten a string
    """
    if instance is None:
        return None

    ignorar = set(ignorar_campos or set()) | IGNORAR_CAMPOS_DEFAULT

    data = model_to_dict(instance)

    # Quitar campos que no aportan
    for campo in list(data.keys()):
        if campo in ignorar:
            data.pop(campo, None)

    # Convertir valores no JSON
    for k, v in data.items():
        try:
            json.dumps(v)
        except TypeError:
            data[k] = str(v)

    return data


def obtener_cambios(instance_before, instance_after, ignorar_campos=None):
    """
    Devuelve solo los campos modificados entre 2 instancias.
    """
    before = modelo_a_dict_seguro(instance_before, ignorar_campos=ignorar_campos)
    after = modelo_a_dict_seguro(instance_after, ignorar_campos=ignorar_campos)

    # Si es creación, before puede ser None
    if before is None or after is None:
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


def registrar_auditoria(
    usuario=None,
    accion="ACCEDER",
    modelo_afectado="",
    registro_id=None,
    cambios_antes=None,
    cambios_despues=None,
    request=None
):
    """
    Registra un evento de auditoría.
    ✅ IP y user_agent centralizados
    """
    AuditoriaLog.objects.create(
        usuario=usuario,
        accion=accion,
        modelo_afectado=modelo_afectado,
        registro_id=registro_id,
        cambios_antes=cambios_antes,
        cambios_despues=cambios_despues,
        ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
