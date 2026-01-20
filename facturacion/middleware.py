from django.shortcuts import redirect

class LoginRequiredMiddleware:

    EXEMPT_PATHS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/no-autorizado/',
        '/admin/',

        # ✅ 2FA: permitir la pantalla de verificación
        '/2fa/verificar/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # ✅ Permitir archivos estáticos y media
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # ✅ Permitir rutas exentas (login, logout, no-autorizado, admin, verify)
        for exempt in self.EXEMPT_PATHS:
            if path.startswith(exempt):
                return self.get_response(request)

        # ✅ Permitir cualquier ruta /2fa/ solo si hay sesión pendiente
        # (evita que cualquiera acceda a /2fa/ sin pasar por login)
        if path.startswith('/2fa/') and request.session.get('pending_2fa_user_id'):
            return self.get_response(request)

        # ✅ Si ya está autenticado, seguir normal
        if request.user.is_authenticated:
            return self.get_response(request)

        # 🚫 Bloquear todo lo demás
        return redirect('acceso_no_autorizado')
