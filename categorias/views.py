from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Categoria
from django.http import HttpResponse

def inicio(request):
    return HttpResponse("Bienvenido al sistema de facturación")

@login_required(login_url='/accounts/login/')
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias/lista.html', {'categorias': categorias})

def crear_categoria(request):
    if request.method == 'POST':
        Categoria.objects.create(nombre=request.POST['nombre'])
        return redirect('lista_categorias')
    return render(request, 'categorias/crear.html')

def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        categoria.nombre = request.POST['nombre']
        categoria.save()
        return redirect('lista_categorias')
    return render(request, 'categorias/editar.html', {'categoria': categoria})

def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    categoria.delete()
    return redirect('lista_categorias')
