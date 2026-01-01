from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CrearUsuarioForm


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
                user.groups.add(grupo)

            return redirect("usuarios:lista")
    else:
        form = CrearUsuarioForm()

    return render(request, "usuarios/crear_usuario.html", {"form": form})


# 🔍 VER usuario
def ver_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    return render(request, "usuarios/ver_usuario.html", {"usuario": usuario})


# ✏️ EDITAR usuario
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = CrearUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect("usuarios:lista")
    else:
        form = CrearUsuarioForm(instance=usuario)

    return render(request, "usuarios/editar_usuario.html", {"form": form, "usuario": usuario})


# 🗑️ ELIMINAR usuario
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    usuario.delete()
    return redirect("usuarios:lista")


