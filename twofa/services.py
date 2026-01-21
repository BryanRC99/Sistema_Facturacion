import secrets
from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings


from .models import EmailOTP

OTP_TTL_MINUTES = 5


def generate_code() -> str:
    return str(secrets.randbelow(1_000_000)).zfill(6)


def create_otp(user):
    """
    Crea un OTP nuevo e invalida los anteriores pendientes.
    Retorna (otp, code) donde code es el código en claro (para enviarlo por email).
    """
    EmailOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    code = generate_code()
    otp = EmailOTP.objects.create(
        user=user,
        code_hash=make_password(code),
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
        is_used=False,
    )
    return otp, code


def _get_client_ip(request) -> str:
    """
    Obtiene IP real si hay proxy (Render, etc). En local suele ser REMOTE_ADDR.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # puede venir: "ip1, ip2, ip3"
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "Desconocida")


def _parse_user_agent(request) -> tuple[str, str]:
    """
    Heurística simple (sin librerías):
    - device: Móvil / Tablet / PC
    - browser: String del User-Agent
    """
    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()

    # dispositivo
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        device = "Móvil"
    elif "ipad" in ua or "tablet" in ua:
        device = "Tablet"
    else:
        device = "PC"

    # navegador (dejamos el UA recortado)
    browser = request.META.get("HTTP_USER_AGENT", "Desconocido")
    if len(browser) > 160:
        browser = browser[:160] + "..."

    return device, browser


def send_otp_email(request, user, code: str):
    subject = "Código de verificación - Sistema de Facturación"
    to = [user.email]

    ip_address = _get_client_ip(request)
    device, browser = _parse_user_agent(request)
    dt_str = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M:%S")

    # ✅ Aquí estaba el error: getattr(settings, "LOGO_URL", "")  (no la URL como key)
    logo_url = getattr(settings, "LOGO_URL", "https://res.cloudinary.com/dmhed5kxh/image/upload/v1769004998/logo_vifmb7.png")

    text = (
        f"Tu código es: {code}. Expira en {OTP_TTL_MINUTES} minutos.\n"
        f"IP: {ip_address}\n"
        f"Dispositivo: {device}\n"
        f"Navegador: {browser}\n"
        f"Fecha: {dt_str}\n"
        "Si no fuiste tú, ignora este correo y cambia tu contraseña."
    )

    html = render_to_string(
        "emails/otp.html",
        {
            "user": user,
            "code": code,
            "ttl": OTP_TTL_MINUTES,
            "year": timezone.now().year,
            "logo_url": logo_url,
            "ip_address": ip_address,
            "device": device,
            "browser": browser,
            "datetime": dt_str,
        },
    )

    msg = EmailMultiAlternatives(subject, text, None, to)
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)


def verify_code(user, code_input: str) -> bool:
    otp = EmailOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
    if not otp:
        return False

    if otp.is_expired():
        otp.is_used = True
        otp.save(update_fields=["is_used"])
        return False

    ok = check_password(code_input, otp.code_hash)
    if ok:
        otp.is_used = True
        otp.save(update_fields=["is_used"])
    return ok
