from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve
from urllib.parse import quote

class LoginRequiredMiddleware:
    EXEMPT_URL_NAMES = {
        "login",
        "logout",
        "password_reset",
        "password_reset_done",
        "password_reset_confirm",
        "password_reset_complete",
    }

    EXEMPT_PREFIXES = (
        "/accounts/login",
        "/accounts/logout",
        "/admin",
        "/static/",
        "/media/",
        "/2fa/",
        "/no-autorizado",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1️⃣ Permitir prefijos
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)

        # 2️⃣ Permitir vistas auth por nombre
        try:
            match = resolve(path)
            if match.url_name in self.EXEMPT_URL_NAMES:
                return self.get_response(request)
        except Exception:
            pass

        # 3️⃣ Si está autenticado, pasar
        if request.user.is_authenticated:
            return self.get_response(request)

        # 4️⃣ Redirigir al login con next
        login_url = settings.LOGIN_URL
        return redirect(f"{login_url}?next={quote(request.get_full_path())}")
