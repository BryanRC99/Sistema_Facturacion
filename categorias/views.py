from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Categoria
from django.http import HttpResponse
from django.contrib import messages


def inicio(request):
    return HttpResponse("Bienvenido al sistema de facturación")

@login_required(login_url='/accounts/login/')
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/lista.html', {'categorias': categorias})

def crear_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('crear_categoria')

        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            messages.warning(request, "Ya existe una categoría con ese nombre.")
            return redirect('crear_categoria')

        Categoria.objects.create(nombre=nombre)
        messages.success(request, "Categoría creada correctamente.")
        return redirect('lista_categorias')

    return render(request, 'categorias/crear.html')

def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect('editar_categoria', id=id)

        if Categoria.objects.filter(nombre__iexact=nombre).exclude(id=id).exists():
            messages.warning(request, "Ya existe otra categoría con ese nombre.")
            return redirect('editar_categoria', id=id)

        categoria.nombre = nombre
        categoria.save()

        messages.success(request, "Categoría actualizada correctamente.")
        return redirect('lista_categorias')

    return render(request, 'categorias/editar.html', {
        'categoria': categoria
    })

def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()

    messages.success(request, "Categoría eliminada correctamente.")
    return redirect('lista_categorias')
