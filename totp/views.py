from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import TOTPProfile
from .services import (
    build_provisioning_uri,
    generate_totp_secret,
    make_qr_base64,
    verify_totp_code,
)

ISSUER_NAME = getattr(settings, "TOTP_ISSUER_NAME", "Sistema de Facturación")


@login_required
@require_http_methods(["GET"])
def totp_setup(request):
    """
    Muestra QR y guarda temporalmente el secret en session hasta confirmar.
    """
    profile, _ = TOTPProfile.objects.get_or_create(user=request.user)

    if profile.enabled and profile.secret:
        messages.info(request, "Google Authenticator ya está activado en tu cuenta.")
        return redirect("usuarios:editar", request.user.id) if _has_usuarios_editar() else redirect("/")

    # Generar secret temporal y guardarlo en sesión
    secret = generate_totp_secret()
    request.session["pending_totp_secret"] = secret

    uri = build_provisioning_uri(
        secret=secret,
        username=request.user.username,
        issuer=ISSUER_NAME,
    )
    qr_b64 = make_qr_base64(uri)

    context = {
        "qr_b64": qr_b64,
        "secret": secret,  # por si quiere ingresarlo manual
        "issuer": ISSUER_NAME,
    }
    return render(request, "totp/setup.html", context)


@login_required
@require_http_methods(["POST"])
def totp_confirm(request):
    """
    Confirma el código y activa TOTP guardando secret en DB.
    """
    profile, _ = TOTPProfile.objects.get_or_create(user=request.user)

    secret = request.session.get("pending_totp_secret")
    code = request.POST.get("code", "")

    if not secret:
        messages.error(request, "No hay un código pendiente. Vuelve a activar Google Authenticator.")
        return redirect("totp:setup")

    if not verify_totp_code(secret, code):
        messages.error(request, "Código inválido. Intenta nuevamente.")
        return redirect("totp:setup")

    profile.secret = secret
    profile.enabled = True
    profile.save(update_fields=["secret", "enabled", "updated_at"])

    # limpiar session
    request.session.pop("pending_totp_secret", None)

    messages.success(request, "Google Authenticator activado correctamente.")
    return _redirect_to_profile_edit(request)


@login_required
@require_http_methods(["POST"])
def totp_disable(request):
    """
    Desactiva TOTP. (Opcional: pedir contraseña o código TOTP antes de desactivar)
    """
    profile, _ = TOTPProfile.objects.get_or_create(user=request.user)

    profile.enabled = False
    profile.secret = None
    profile.save(update_fields=["enabled", "secret", "updated_at"])

    messages.success(request, "Google Authenticator desactivado.")
    return _redirect_to_profile_edit(request)


def _redirect_to_profile_edit(request):
    # Si tienes namespace usuarios:editar, redirige ahí; si no, vuelve a /
    return redirect("usuarios:editar", request.user.id) if _has_usuarios_editar() else redirect("/")


def _has_usuarios_editar():
    """
    Evita error si el nombre de la ruta difiere.
    Si tu ruta se llama exactamente usuarios:editar, esto sirve.
    """
    return True
