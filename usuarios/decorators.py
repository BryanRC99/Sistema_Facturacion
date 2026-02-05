from functools import wraps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


DEFAULT_403_CONTEXT = {
    "title": "Acceso no autorizado",
    "message": "Tu cuenta no tiene permisos para realizar esta acción o acceder a esta sección.",
}


def group_required(group_names, template_name="403.html"):
    """
    Permite acceso solo a usuarios que pertenezcan a uno de los grupos indicados.
    group_names puede ser un string ("SuperAdmin") o una lista (["Vendedor","SuperAdmin"]).
    """
    if isinstance(group_names, str):
        group_names = [group_names]

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)

            return render(request, template_name, DEFAULT_403_CONTEXT, status=403)

        return _wrapped_view

    return decorator


def profile_edit_required(superadmin_group="SuperAdmin", template_name="403.html"):
    """
    Permite:
    - SuperAdmin: editar cualquier usuario
    - Usuario normal (ej: Vendedor): solo su propio perfil (id de la URL == request.user.id)
    Requiere que la vista reciba user_id (por kwargs o por args).
    """

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Tomar user_id desde kwargs o desde el primer arg posicional
            user_id = kwargs.get("user_id")
            if user_id is None and len(args) > 0:
                user_id = args[0]

            # Si por alguna razón no viene user_id, mejor bloquear
            if user_id is None:
                return render(request, template_name, DEFAULT_403_CONTEXT, status=403)

            # SuperAdmin puede editar a cualquiera
            if request.user.groups.filter(name=superadmin_group).exists():
                return view_func(request, *args, **kwargs)

            # Solo puede editarse a sí mismo
            try:
                if int(user_id) == request.user.id:
                    return view_func(request, *args, **kwargs)
            except (TypeError, ValueError):
                pass

            ctx = {
                "title": "Acceso no autorizado",
                "message": "No puedes editar el perfil de otro usuario.",
            }
            return render(request, template_name, ctx, status=403)

        return _wrapped_view

    return decorator
