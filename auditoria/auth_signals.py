# auditoria/auth_signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from auditoria.utils import registrar_auditoria, get_client_ip, get_user_agent


def resumir_dispositivo(user_agent: str | None) -> dict:
    """
    Resumen simple (sin librerías extra) a partir del User-Agent.
    No es perfecto, pero sirve para dashboard.
    """
    ua = (user_agent or "").lower()

    # OS
    if "windows" in ua:
        os_name = "Windows"
    elif "android" in ua:
        os_name = "Android"
    elif "iphone" in ua or "ipad" in ua or "ios" in ua:
        os_name = "iOS"
    elif "mac os x" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        os_name = "Linux"
    else:
        os_name = "Desconocido"

    # Browser
    # (orden importa para no confundir Edge/Chrome)
    if "edg/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "chromium" not in ua and "edg/" not in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    else:
        browser = "Desconocido"

    # Tipo de dispositivo (aprox)
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        device = "Móvil"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    else:
        device = "PC"

    return {"dispositivo": device, "sistema": os_name, "navegador": browser}


@receiver(user_logged_in)
def auditoria_login(sender, request, user, **kwargs):
    ua = get_user_agent(request)
    ip = get_client_ip(request)

    # Guardamos un resumen en cambios_despues para que sea legible en dashboard
    resumen = resumir_dispositivo(ua)
    resumen.update({"ip": ip})

    registrar_auditoria(
        usuario=user,
        accion="LOGIN",
        modelo_afectado="Auth",
        registro_id=user.id,
        cambios_antes=None,
        cambios_despues=resumen,   # ✅ aquí va lo legible
        request=request            # ✅ aquí se guarda ip + user_agent también
    )
