from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor


def lista_proveedores(request):
    proveedores = Proveedor.objects.all()

    # Para mostrar el texto del choice (RUC, Cédula, etc.)
    for p in proveedores:
        p.tipo_identificacion_display = p.get_tipo_identificacion_display()

    return render(request, 'proveedores/lista.html', {
        'proveedores': proveedores
    })


def crear_proveedor(request):
    if request.method == 'POST':

        identificacion = request.POST['identificacion']

        # Validación: identificación duplicada
        if Proveedor.objects.filter(identificacion=identificacion).exists():
            return render(request, 'proveedores/crear.html', {
                "error": "Ya existe un proveedor con esta identificación.",
                "form_data": request.POST
            })

        Proveedor.objects.create(
            tipo_identificacion=request.POST['tipo_identificacion'],
            identificacion=identificacion,
            nombre_razon_social=request.POST['nombre_razon_social'],
            telefono=request.POST['telefono'],
            celular=request.POST['celular'],
            direccion=request.POST['direccion'],
            correo=request.POST['correo'],
            ciudad=request.POST.get('ciudad'),
            contacto_nombre=request.POST.get('contacto_nombre'),
            contacto_telefono=request.POST.get('contacto_telefono'),
            observaciones=request.POST.get('observaciones'),
        )

        return redirect('lista_proveedores')

    return render(request, 'proveedores/crear.html')



def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':

        nueva_identificacion = request.POST['identificacion']

        # Validación: evitar identificación duplicada
        if Proveedor.objects.filter(identificacion=nueva_identificacion) \
                            .exclude(id=proveedor.id).exists():
            return render(request, 'proveedores/editar.html', {
                "proveedor": proveedor,
                "error": "Otro proveedor ya está utilizando esta identificación.",
                "form_data": request.POST
            })

        proveedor.tipo_identificacion = request.POST['tipo_identificacion']
        proveedor.identificacion = nueva_identificacion
        proveedor.nombre_razon_social = request.POST['nombre_razon_social']
        proveedor.telefono = request.POST.get('telefono')
        proveedor.celular = request.POST.get('celular')
        proveedor.direccion = request.POST['direccion']
        proveedor.correo = request.POST.get('correo')
        proveedor.contacto_nombre = request.POST.get('contacto')  # Correcto aquí
        proveedor.contacto_telefono = request.POST.get('contacto_telefono')  # Correcto aquí
        proveedor.ciudad = request.POST.get('ciudad')  # Si tienes este campo en tu formulario
        proveedor.observaciones = request.POST.get('observaciones')  # Si tienes este campo en tu formulario
        proveedor.save()

        return redirect('lista_proveedores')

    return render(request, 'proveedores/editar.html', {
        'proveedor': proveedor
    })



def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    proveedor.delete()
    return redirect('lista_proveedores')
