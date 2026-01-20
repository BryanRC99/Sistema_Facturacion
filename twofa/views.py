from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .services import create_otp, send_otp_email, verify_code
from .utils import set_trusted_cookie, clear_trusted_cookie

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
        return redirect("login")

    if request.method == "POST":
        action = request.POST.get("action", "verify").strip()

        # ✅ Reenviar código
        if action == "resend":
            remaining = _cooldown_remaining_seconds(request)
            if remaining > 0:
                messages.error(request, f"Espera {remaining}s para reenviar el código.")
            else:
                otp, code = create_otp(user)
                send_otp_email(user, code)
                request.session["otp_last_sent_ts"] = int(timezone.now().timestamp())
                messages.success(request, "Se envió un nuevo código a tu correo.")
            return redirect("/2fa/verificar/")

        # ✅ Verificar código OTP
        code_input = request.POST.get("code", "").strip()

        # ✅ Validación fuerte: exactamente 6 dígitos numéricos
        if len(code_input) != 6 or not code_input.isdigit():
            messages.error(request, "Ingresa los 6 dígitos del código.")
            return redirect("/2fa/verificar/")

        if verify_code(user, code_input):
            login(request, user)

            # Limpiar datos temporales de 2FA
            request.session.pop("pending_2fa_user_id", None)
            request.session.pop("otp_last_sent_ts", None)

            response = redirect("/")  # dashboard / inicio

            # ✅ Confiar en este dispositivo (cookie)
            if request.POST.get("trust_device") == "on":
                set_trusted_cookie(response, user.id)

            messages.success(request, "Verificación correcta.")
            return response

        # ❌ Código incorrecto
        messages.error(request, "Código incorrecto o expirado.")
        return redirect("/2fa/verificar/")

    remaining = _cooldown_remaining_seconds(request)

    return render(
        request,
        "twofa/verify.html",
        {
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
