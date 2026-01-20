# auditoria/middleware.py
import threading
from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


def get_current_user():
    req = get_current_request()
    if req and hasattr(req, "user") and req.user.is_authenticated:
        return req.user
    return None


class AuditoriaMiddleware(MiddlewareMixin):
    """
    ✅ SOLO guarda el request actual para que signals pueda leer:
       - usuario autenticado
       - IP
       - user-agent

    ❌ NO registra logs aquí (para evitar duplicados).
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Guardar request cuando ya pasaron middlewares previos (auth incluido)
        _thread_locals.request = request
        return None

    def process_response(self, request, response):
        if hasattr(_thread_locals, "request"):
            delattr(_thread_locals, "request")
        return response

    def process_exception(self, request, exception):
        if hasattr(_thread_locals, "request"):
            delattr(_thread_locals, "request")
        return None


