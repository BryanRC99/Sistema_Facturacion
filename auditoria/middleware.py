from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from auditoria.models import AuditoriaLog


class AuditoriaMiddleware(MiddlewareMixin):
    """
    Middleware para registrar acceso y acciones
    ejecutadas por los usuarios en el sistema.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # No registrar acceso a archivos estáticos
        if request.path.startswith('/static/'):
            return None

        # Si el usuario no está autenticado, no registrar nada
        usuario = request.user if request.user.is_authenticated else None
        if not usuario:
            return None

        # Registrar solo acciones relevantes
        metodo = request.method
        es_modificacion = metodo in ['POST', 'PUT', 'PATCH', 'DELETE']
        es_lectura_detalle = metodo == 'GET' and 'pk' in view_kwargs  # GET para objetos específicos

        if not (es_modificacion or es_lectura_detalle):
            return None

        # Obtener IP real del cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # Crear registro en la auditoria
        AuditoriaLog.objects.create(
            usuario=usuario,
            accion=f"{metodo} {view_func.__name__}",
            modelo_afectado=f"{view_func.__module__}.{view_func.__name__}",
            registro_id=view_kwargs.get('pk'),
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', 'Unknown'),
            fecha=timezone.now()
        )

        return None



