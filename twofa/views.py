from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .services import create_otp, send_otp_email, verify_code
from .utils import set_trusted_cookie, clear_trusted_cookie

# ✅ TOTP (Google Authenticator)
from totp.models import TOTPProfile
from totp.services import verify_totp_code

User = get_user_model()

RESEND_COOLDOWN_SECONDS = 60  # 1 minuto


def mask_email(email: str) -> str:
    try:
        name, domain = email.split("@", 1)
        if len(name) <= 2:
            return "*" * len(name) + "@" + domain
        return name[:2] + ("*" * max(2, len(name) - 4)) + name[-2:] + "@" + domain
    except Exception:
        return email


def _cooldown_remaining_seconds(request) -> int:
    ts = request.session.get("otp_last_sent_ts")
    if not ts:
        return 0
    now_ts = int(timezone.now().timestamp())
    remaining = RESEND_COOLDOWN_SECONDS - (now_ts - int(ts))
    return max(0, remaining)


def _get_next_url(request) -> str:
    # ✅ Viene desde auth_views.py
    return request.session.pop("pending_2fa_next", "/") or "/"


@require_http_methods(["GET", "POST"])
def verify_2fa(request):
    # ✅ Si es GET, limpia mensajes anteriores entrando a la vista
    if request.method == "GET":
        list(messages.get_messages(request))

    user_id = request.session.get("pending_2fa_user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.pop("pending_2fa_user_id", None)
        request.session.pop("otp_last_sent_ts", None)
        request.session.pop("pending_2fa_next", None)
        return redirect("login")

    # ✅ Saber si el usuario tiene Google Authenticator activo
    totp_profile, _ = TOTPProfile.objects.get_or_create(user=user)
    has_totp = bool(totp_profile.enabled and totp_profile.secret)

    # ✅ Método solicitado: totp o email
    method = (request.GET.get("m") or "email").strip().lower()
    if method not in ("totp", "email"):
        method = "email"
    if method == "totp" and not has_totp:
        method = "email"

    if request.method == "POST":
        action = (request.POST.get("action") or "verify").strip()

        # ✅ Cambiar a correo (desde TOTP). Envía OTP solo cuando el usuario lo pide.
        if action == "use_email":
            if not user.email:
                messages.error(request, "Tu usuario no tiene email registrado. No se puede usar 2FA por correo.")
                return redirect("login")

            remaining = _cooldown_remaining_seconds(request)
            if remaining > 0:
                messages.error(request, f"Espera {remaining}s para enviar el código.")
            else:
                _otp, code = create_otp(user)
                send_otp_email(request, user, code)  # ✅ FIX: requiere request
                request.session["otp_last_sent_ts"] = int(timezone.now().timestamp())
                messages.success(request, "Se envió un código a tu correo.")
            return redirect("/2fa/verificar/?m=email")

        # ✅ Reenviar código (solo email)
        if action == "resend":
            if not user.email:
                messages.error(request, "Tu usuario no tiene email registrado. No se puede reenviar el código.")
                return redirect("login")

            remaining = _cooldown_remaining_seconds(request)
            if remaining > 0:
                messages.error(request, f"Espera {remaining}s para reenviar el código.")
            else:
                _otp, code = create_otp(user)
                send_otp_email(request, user, code)  # ✅ FIX: requiere request
                request.session["otp_last_sent_ts"] = int(timezone.now().timestamp())
                messages.success(request, "Se envió un nuevo código a tu correo.")
            return redirect("/2fa/verificar/?m=email")

        # ✅ Verificar código (TOTP o Email)
        code_input = (request.POST.get("code") or "").strip().replace(" ", "")

        # ✅ Validación fuerte: exactamente 6 dígitos numéricos
        if len(code_input) != 6 or not code_input.isdigit():
            messages.error(request, "Ingresa los 6 dígitos del código.")
            return redirect(f"/2fa/verificar/?m={method}")

        # ====== Verificación TOTP (Google Authenticator) ======
        if method == "totp":
            if verify_totp_code(totp_profile.secret, code_input):
                login(request, user)

                # Limpiar datos temporales de 2FA
                request.session.pop("pending_2fa_user_id", None)
                request.session.pop("otp_last_sent_ts", None)

                next_url = _get_next_url(request)
                response = redirect(next_url)

                # ✅ Confiar en este dispositivo (cookie)
                if request.POST.get("trust_device") == "on":
                    set_trusted_cookie(response, user.id)

                messages.success(request, "Verificación correcta.")
                return response

            messages.error(request, "Código de Google Authenticator incorrecto.")
            return redirect("/2fa/verificar/?m=totp")

        # ====== Verificación Email OTP (Brevo) ======
        if verify_code(user, code_input):
            login(request, user)

            # Limpiar datos temporales de 2FA
            request.session.pop("pending_2fa_user_id", None)
            request.session.pop("otp_last_sent_ts", None)

            next_url = _get_next_url(request)
            response = redirect(next_url)

            # ✅ Confiar en este dispositivo (cookie)
            if request.POST.get("trust_device") == "on":
                set_trusted_cookie(response, user.id)

            messages.success(request, "Verificación correcta.")
            return response

        # ❌ Código incorrecto
        messages.error(request, "Código incorrecto o expirado.")
        return redirect("/2fa/verificar/?m=email")

    # GET: contexto para el template
    remaining = _cooldown_remaining_seconds(request) if method == "email" else 0

    return render(
        request,
        "twofa/verify.html",
        {
            "method": method,              # "totp" o "email"
            "has_totp": has_totp,          # True si tiene Authenticator activo
            "email_masked": mask_email(user.email),
            "cooldown_seconds": remaining,
        },
    )


@login_required
@require_POST
def forget_device(request):
    response = redirect("/")  # o donde quieras
    clear_trusted_cookie(response)
    messages.success(request, "Este dispositivo dejó de ser confiable.")
    return response
