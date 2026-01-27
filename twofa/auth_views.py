from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from totp.models import TOTPProfile
from .services import create_otp, send_otp_email
from .utils import is_trusted_device

RESEND_COOLDOWN_SECONDS = 60  # 1 minuto


@require_http_methods(["GET", "POST"])
def login_with_2fa(request):
    form = AuthenticationForm(request, data=request.POST or None)

    # ✅ Capturar next (GET o POST) para redirigir luego del 2FA
    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        if not form.is_valid():
            return render(request, "registration/login.html", {"form": form, "next": next_url})

        user = form.get_user()

        # ✅ Si este navegador ya es confiable para este usuario, saltar 2FA
        if is_trusted_device(request, user.id):
            login(request, user)
            return redirect(next_url)

        if not user.email:
            messages.error(request, "Tu usuario no tiene email registrado. No se puede usar 2FA por correo.")
            return render(request, "registration/login.html", {"form": form, "next": next_url})

        # Guardar usuario pendiente 2FA en sesión
        request.session["pending_2fa_user_id"] = user.id
        request.session["pending_2fa_next"] = next_url  # ✅ para usarlo al final en verify_2fa

        # ✅ Si Authenticator está activo -> NO mandar correo. Va directo a verificar TOTP
        totp_profile, _ = TOTPProfile.objects.get_or_create(user=user)
        if totp_profile.enabled and totp_profile.secret:
            return redirect("/2fa/verificar/?m=totp")

        # ✅ Si NO hay Authenticator -> manda OTP por correo y va a verificar email
        _otp, code = create_otp(user)
        send_otp_email(request, user, code)
        request.session["otp_last_sent_ts"] = int(timezone.now().timestamp())

        # Limpia mensajes viejos
        list(messages.get_messages(request))

        return redirect("/2fa/verificar/?m=email")

    return render(request, "registration/login.html", {"form": form, "next": next_url})
