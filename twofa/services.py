import secrets
from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

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


def send_otp_email(user, code: str):
    subject = "Código de verificación - Sistema de Facturación"
    to = [user.email]

    text = f"Tu código es: {code}. Expira en {OTP_TTL_MINUTES} minutos."
    html = render_to_string(
        "emails/otp.html",
        {
            "user": user,
            "code": code,
            "ttl": OTP_TTL_MINUTES,
            "year": timezone.now().year,
        },
    )

    msg = EmailMultiAlternatives(subject, text, None, to)
    msg.attach_alternative(html, "text/html")
    msg.send()


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
