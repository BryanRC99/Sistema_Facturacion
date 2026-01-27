from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearUsuarioForm
from .forms import EditarUsuarioForm
from django.contrib import messages
from django.contrib.auth.models import User


def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, "usuarios/lista.html", {"usuarios": usuarios})


def crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuarioForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            grupo = form.cleaned_data.get("grupo")
            user.save()

            if grupo:
                user.groups.set([grupo])  # deja solo ese grupo (si prefieres add(), dime)
            else:
                user.groups.clear()

            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuarios:lista")

        # Form inválido
        messages.error(request, "Revisa los datos del formulario.")
        return render(request, "usuarios/crear_usuario.html", {"form": form})

    form = CrearUsuarioForm()
    return render(request, "usuarios/crear_usuario.html", {"form": form})


def ver_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    return render(request, "usuarios/ver_usuario.html", {"usuario": usuario})


def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            grupo = form.cleaned_data.get("grupo")

            if grupo:
                user.groups.set([grupo])
            else:
                user.groups.clear()

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("usuarios:lista")

        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, "usuarios/editar_usuario.html", {"form": form, "usuario": usuario})

def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    # Evitar que se elimine a sí mismo
    if request.user.is_authenticated and request.user.id == usuario.id:
        messages.error(request, "No puedes eliminar tu propio usuario mientras estás autenticado.")
        return redirect("usuarios:lista")

    username = usuario.username
    usuario.delete()
    messages.success(request, f"Usuario '{username}' eliminado correctamente.")
    return redirect("usuarios:lista")

