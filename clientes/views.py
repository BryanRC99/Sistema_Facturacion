from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cliente


def lista_clientes(request):
    clientes = Cliente.objects.all()
    for c in clientes:
        c.tipo_identificacion_display = c.get_tipo_identificacion_display()
    return render(request, 'clientes/lista.html', {'clientes': clientes})


def crear_cliente(request):
    if request.method == 'POST':
        form_data = request.POST

        tipo_identificacion = request.POST.get('tipo_identificacion', '').strip()
        identificacion = request.POST.get('identificacion', '').strip()
        nombre_razon_social = request.POST.get('nombre_razon_social', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        celular = request.POST.get('celular', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        correo = request.POST.get('correo', '').strip()

        # =========================
        # VALIDACIONES
        # =========================
        if not tipo_identificacion:
            messages.error(request, "Debes seleccionar el tipo de identificación.")
            return render(request, 'clientes/crear.html', {"form_data": form_data})

        if not identificacion:
            messages.error(request, "La identificación es obligatoria.")
            return render(request, 'clientes/crear.html', {"form_data": form_data})

        if not nombre_razon_social:
            messages.error(request, "El nombre o razón social es obligatorio.")
            return render(request, 'clientes/crear.html', {"form_data": form_data})

        # Validación de identificación duplicada (ignora mayúsculas/minúsculas)
        if Cliente.objects.filter(identificacion__iexact=identificacion).exists():
            messages.warning(request, "Ya existe un cliente con esta identificación.")
            return render(request, 'clientes/crear.html', {"form_data": form_data})

        # (Opcional) Validación rápida de correo (sin regex pesada)
        if correo and ("@" not in correo or "." not in correo):
            messages.error(request, "El correo no parece válido.")
            return render(request, 'clientes/crear.html', {"form_data": form_data})

        # =========================
        # CREAR
        # =========================
        Cliente.objects.create(
            tipo_identificacion=tipo_identificacion,
            identificacion=identificacion,
            nombre_razon_social=nombre_razon_social,
            telefono=telefono,
            celular=celular,
            direccion=direccion,
            correo=correo,
        )

        messages.success(request, "Cliente creado correctamente.")
        return redirect('lista_clientes')

    return render(request, 'clientes/crear.html')


def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        form_data = request.POST

        tipo_identificacion = request.POST.get('tipo_identificacion', '').strip()
        nueva_identificacion = request.POST.get('identificacion', '').strip()
        nombre_razon_social = request.POST.get('nombre_razon_social', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        celular = request.POST.get('celular', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        correo = request.POST.get('correo', '').strip()

        # =========================
        # VALIDACIONES
        # =========================
        if not tipo_identificacion:
            messages.error(request, "Debes seleccionar el tipo de identificación.")
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "form_data": form_data
            })

        if not nueva_identificacion:
            messages.error(request, "La identificación es obligatoria.")
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "form_data": form_data
            })

        if not nombre_razon_social:
            messages.error(request, "El nombre o razón social es obligatorio.")
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "form_data": form_data
            })

        # Que no exista otro con la misma identificación
        if Cliente.objects.filter(identificacion__iexact=nueva_identificacion).exclude(id=cliente.id).exists():
            messages.warning(request, "Otro cliente ya está utilizando esta identificación.")
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "form_data": form_data
            })

        if correo and ("@" not in correo or "." not in correo):
            messages.error(request, "El correo no parece válido.")
            return render(request, 'clientes/editar.html', {
                "cliente": cliente,
                "form_data": form_data
            })

        # =========================
        # GUARDAR
        # =========================
        cliente.tipo_identificacion = tipo_identificacion
        cliente.identificacion = nueva_identificacion
        cliente.nombre_razon_social = nombre_razon_social
        cliente.telefono = telefono
        cliente.celular = celular
        cliente.direccion = direccion
        cliente.correo = correo

        # Auditoría (lo mantengo tal cual lo tenías)
        cliente._auditoria_user = request.user

        cliente.save()
        messages.success(request, "Cliente actualizado correctamente.")
        return redirect('lista_clientes')

    return render(request, 'clientes/editar.html', {'cliente': cliente})


def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    messages.success(request, "Cliente eliminado correctamente.")
    return redirect('lista_clientes')
