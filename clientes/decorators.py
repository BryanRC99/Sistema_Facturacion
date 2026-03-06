from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def cliente_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        # 1️⃣ No autenticado
        if not request.user.is_authenticated:
            return redirect("login_cliente")

        # 2️⃣ No tiene cuenta cliente
        if not hasattr(request.user, "cliente_account"):
            messages.error(request, "No tienes acceso al portal de clientes.")
            return redirect("acceso_no_autorizado")

        # 3️⃣ Cuenta desactivada
        if not request.user.cliente_account.activo:
            messages.error(request, "Tu cuenta de cliente está desactivada.")
            return redirect("acceso_no_autorizado")  # 🔥 CAMBIO AQUÍ

        return view_func(request, *args, **kwargs)

    return _wrapped
