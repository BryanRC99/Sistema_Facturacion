from django.shortcuts import redirect

class LoginRequiredMiddleware:

    # Rutas que no requieren login
    EXEMPT_PATHS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/no-autorizado/',
        '/admin/',        # admin_guard
        '/django-admin/', # admin real Django
        '/2fa/verificar/',
        '/2fa/',
        '/portal-clientes/login/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Permitir static y media
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # Permitir rutas exentas
        for exempt in self.EXEMPT_PATHS:
            if path.startswith(exempt):
                return self.get_response(request)

        # Permitir 2FA si hay sesión pendiente
        if path.startswith('/2fa/') and request.session.get('pending_2fa_user_id'):
            return self.get_response(request)

        # Redirigir si no está autenticado
        if not request.user.is_authenticated:
            return redirect('acceso_no_autorizado')

        # ===============================
        # AISLAMIENTO POR ROL
        # ===============================

        # CLIENTE
        if request.user.groups.filter(name="Clientes").exists():
            # Solo pueden entrar a portal-clientes
            if not path.startswith('/portal-clientes/'):
                return redirect('portal_cliente')  # Asegúrate que esta vista existe

        # SUPERADMIN / VENDEDOR
        elif request.user.groups.filter(name__in=["SuperAdmin", "Vendedor"]).exists():
            # 🔹 Pueden acceder a todos los módulos internos
            pass  # No bloqueamos ninguna ruta

        # Otros usuarios (si los hay)
        else:
            # Redirigir a no autorizado si intentan acceder a módulos internos
            if path.startswith((
                '/clientes/', '/productos/', '/categorias/', '/proveedores/',
                '/facturas/', '/reportes/', '/usuarios/', '/auditoria/'
            )):
                return redirect('acceso_no_autorizado')

        # Si pasa todas las validaciones, continuar
        return self.get_response(request)