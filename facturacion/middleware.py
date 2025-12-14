from django.shortcuts import redirect

class LoginRequiredMiddleware:

    EXEMPT_PATHS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/no-autorizado/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            return self.get_response(request)

        # Permitir rutas exentas
        for path in self.EXEMPT_PATHS:
            if request.path.startswith(path):
                return self.get_response(request)

        # Permitir archivos estáticos
        if request.path.startswith('/static/'):
            return self.get_response(request)

        # 🚫 Bloquear todo lo demás
        return redirect('acceso_no_autorizado')
