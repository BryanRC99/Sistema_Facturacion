from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import quote

class LoginRequiredMiddleware:
    EXEMPT_PREFIXES = [
        "/accounts/login",
        "/accounts/logout",
        "/no-autorizado",
        "/admin",
        "/static/",
        "/media/",
        "/2fa/verificar",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Permitir rutas exentas (con o sin slash)
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)

        # Permitir /2fa/ solo si hay sesión pendiente
        if path.startswith("/2fa/") and request.session.get("pending_2fa_user_id"):
            return self.get_response(request)

        # Si ya está autenticado, seguir normal
        if request.user.is_authenticated:
            return self.get_response(request)

        # Si no está autenticado: mandar al login con next
        login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
        return redirect(f"{login_url}?next={quote(request.get_full_path())}")

