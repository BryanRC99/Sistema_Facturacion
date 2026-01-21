from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .services import create_otp, send_otp_email
from .utils import is_trusted_device

RESEND_COOLDOWN_SECONDS = 60  # 1 minuto


@require_http_methods(["GET", "POST"])
def login_with_2fa(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "registration/login.html")

        # ✅ Si este navegador ya es confiable para este usuario, saltar 2FA
        if is_trusted_device(request, user.id):
            login(request, user)
            return redirect("/")

        if not user.email:
            messages.error(request, "Tu usuario no tiene email registrado. No se puede usar 2FA.")
            return render(request, "registration/login.html")

        otp, code = create_otp(user)
        send_otp_email(request, user, code)

        # ✅ Guardar datos en sesión y forzar creación de sessionid
        request.session["pending_2fa_user_id"] = user.id
        request.session["otp_last_sent_ts"] = int(timezone.now().timestamp())
        request.session.modified = True  # <-- CLAVE para que Render setee sessionid

        return redirect("/2fa/verificar/")

    return render(request, "registration/login.html")


