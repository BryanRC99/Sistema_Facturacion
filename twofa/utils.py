import secrets
from django.conf import settings
from django.utils import timezone

COOKIE_NAME = "trusted_device"

def make_device_token() -> str:
    return secrets.token_urlsafe(32)

def trust_max_age_seconds() -> int:
    return int(getattr(settings, "TRUST_DEVICE_DAYS", 30) * 24 * 60 * 60)

def is_trusted_device(request, user_id: int) -> bool:
    """
    Cookie firmada: "<user_id>:<token>"
    Solo valida que exista, que sea del user y que esté firmada por Django.
    (Para proyecto escolar es suficiente; más abajo te digo cómo subir seguridad.)
    """
    try:
        value = request.get_signed_cookie(COOKIE_NAME, default=None, salt="twofa.trust")
        if not value:
            return False
        uid, _token = value.split(":", 1)
        return int(uid) == int(user_id)
    except Exception:
        return False

def set_trusted_cookie(response, user_id: int):
    token = make_device_token()
    value = f"{user_id}:{token}"
    response.set_signed_cookie(
        COOKIE_NAME,
        value,
        salt="twofa.trust",
        max_age=trust_max_age_seconds(),
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,  # en producción True (https)
    )

def clear_trusted_cookie(response):
    response.delete_cookie(COOKIE_NAME)
