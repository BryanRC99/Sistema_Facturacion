from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente

def lista_clientes(request):
    clientes = Cliente.objects.all()
    for c in clientes:
        c.tipo_identificacion_display = c.get_tipo_identificacion_display()
    return render(request, 'clientes/lista.html', {'clientes': clientes})


def crear_cliente(request):
    if request.method == 'POST':

        identificacion = request.POST['identificacion']

        # Validación de identificación duplicada
        if Cliente.objects.filter(identificacion=identificacion).exists():
            return render(request, 'clientes/crear.html', {
                "error": "Ya existe un cliente con esta identificación.",
                "form_data": request.POST
            })

        # Crear si todo está bien
        Cliente.objects.create(
            tipo_identificacion=request.POST['tipo_identificacion'],
            identificacion=identificacion,
            nombre_razon_social=request.POST['nombre_razon_social'],
            telefono=request.POST['telefono'],
            celular=request.POST['celular'],
            direccion=request.POST['direccion'],
            correo=request.POST['correo'],
        )
        return redirect('lista_clientes')

    return render(request, 'clientes/crear.html')


def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':

        nueva_identificacion = request.POST['identificacion']

        # Validación: que no exista otro cliente con esa identificación
        if Cliente.objects.filter(identificacion=nueva_identificacion)\
                           .exclude(id=cliente.id).exists():
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "error": "Otro cliente ya está utilizando esta identificación.",
                "form_data": request.POST
            })

        # Guardar cambios
        cliente.tipo_identificacion = request.POST['tipo_identificacion']
        cliente.identificacion = nueva_identificacion
        cliente.nombre_razon_social = request.POST['nombre_razon_social']
        cliente.telefono = request.POST['telefono']
        cliente.celular = request.POST['celular']
        cliente.direccion = request.POST['direccion']
        cliente.correo = request.POST['correo']
        cliente.save()

        return redirect('lista_clientes')

    return render(request, 'clientes/editar.html', {'cliente': cliente})


def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return redirect('lista_clientes')

