from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CrearUsuarioForm, EditarUsuarioForm, CustomPasswordChangeForm
from usuarios.decorators import group_required, profile_edit_required
from django.contrib.auth import logout
from django.urls import reverse



@group_required("SuperAdmin")
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "usuarios/lista.html", {"usuarios": usuarios})


@group_required("SuperAdmin")
def crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuarioForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            grupo = form.cleaned_data.get("grupo")
            user.save()

            if grupo:
                user.groups.set([grupo])
            else:
                user.groups.clear()

            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuarios:lista")

        messages.error(request, "Revisa los datos del formulario.")
        return render(request, "usuarios/crear_usuario.html", {"form": form})

    form = CrearUsuarioForm()
    return render(request, "usuarios/crear_usuario.html", {"form": form})


@group_required("SuperAdmin")
def ver_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    return render(request, "usuarios/ver_usuario.html", {"usuario": usuario})


@profile_edit_required()
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    is_superadmin = request.user.groups.filter(name="SuperAdmin").exists()

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)

        if form.is_valid():
            user = form.save(commit=False)

            # 🔒 Si NO es superadmin, NO se permite cambiar grupo
            if is_superadmin:
                user.save()
                grupo = form.cleaned_data.get("grupo")
                if grupo:
                    user.groups.set([grupo])
                else:
                    user.groups.clear()
            else:
                # Guarda el usuario ignorando cualquier intento de manipular el grupo
                user.save()

            messages.success(request, "Perfil actualizado correctamente.")

            # ✅ Redirección según rol
            if is_superadmin:
                return redirect("usuarios:lista")
            return redirect("usuarios:editar", request.user.id)

        messages.error(request, "Revisa los datos del formulario.")

    else:
        form = EditarUsuarioForm(instance=usuario)

        # Opcional: ocultar el campo grupo al no-superadmin
        if not is_superadmin and "grupo" in form.fields:
            form.fields.pop("grupo")

    return render(
        request,
        "usuarios/editar_usuario.html",
        {"form": form, "usuario": usuario},
    )


@group_required("SuperAdmin")
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.user.id == usuario.id:
        messages.error(request, "No puedes eliminar tu propio usuario mientras estás autenticado.")
        return redirect("usuarios:lista")

    username = usuario.username
    usuario.delete()
    messages.success(request, f"Usuario '{username}' eliminado correctamente.")
    return redirect("usuarios:lista")


@login_required
def admin_guard(request):
    # SuperAdmin -> admin real
    if request.user.is_superuser or request.user.groups.filter(name="SuperAdmin").exists():
        return redirect("/django-admin/")

    # No autorizado -> tu 403 bonito
    return render(request, "403.html", status=403)

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import CustomPasswordChangeForm


@login_required
def cambiar_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()

            # ✅ bandera en sesión para cerrar luego
            request.session["force_logout_after_password_change"] = True

            return render(request, "usuarios/password_cambiada.html", {
                "redirect_url": reverse("usuarios:password_logout"),
                "seconds": 5,
            })

        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, "usuarios/cambiar_password.html", {"form": form})

@login_required
def cerrar_sesion_post_password(request):
    if request.session.get("force_logout_after_password_change"):
        request.session.pop("force_logout_after_password_change", None)
        logout(request)
    return redirect(reverse("login"))

