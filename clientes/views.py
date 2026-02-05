from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.contrib.auth.decorators import login_required
from .models import Cliente
from django.template.loader import render_to_string
from weasyprint import HTML
from django.utils import timezone
from usuarios.decorators import group_required



@group_required(["Vendedor", "SuperAdmin"])
def lista_clientes(request):
    clientes = Cliente.objects.all()
    for c in clientes:
        c.tipo_identificacion_display = c.get_tipo_identificacion_display()
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@group_required(["Vendedor", "SuperAdmin"])
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



@group_required(["Vendedor", "SuperAdmin"])
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



@group_required(["Vendedor", "SuperAdmin"])
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    messages.success(request, "Cliente eliminado correctamente.")
    return redirect('lista_clientes')



@group_required(["Vendedor", "SuperAdmin"])
def export_clientes_pdf(request):
    clientes = Cliente.objects.all().order_by("id")

    html_string = render_to_string(
        "clientes/export_pdf.html",  # ✅ coincide con tu estructura
        {
            "clientes": clientes,
            "fecha": timezone.localtime().strftime("%d/%m/%Y %H:%M"),
        }
    )

    pdf_bytes = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/") 
    ).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="clientes.pdf"'
    return response


@group_required(["Vendedor", "SuperAdmin"])
def export_clientes_excel(request):
    clientes = Cliente.objects.all().order_by("id")

    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes"

    # Encabezados (según tus campos reales)
    headers = [
        "#",
        "Tipo Identificación",
        "Identificación",
        "Nombre / Razón Social",
        "Teléfono",
        "Celular",
        "Dirección",
        "Correo",
    ]
    ws.append(headers)

    # Estilo header
    header_fill = PatternFill("solid", fgColor="1F2937")  # gris oscuro
    header_font = Font(bold=True, color="FFFFFF")
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Congelar encabezado y filtro
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    # Filas
    for i, c in enumerate(clientes, start=1):
        ws.append([
            i,
            c.tipo_identificacion,
            c.identificacion,
            c.nombre_razon_social,
            c.telefono,
            c.celular,
            c.direccion,
            c.correo,
        ])

    # Ajustar ancho de columnas
    for col_idx in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for cell in ws[col_letter]:
            val = "" if cell.value is None else str(cell.value)
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max_len + 2, 50)

    # Nombre archivo con fecha
    filename = f"clientes_{timezone.localtime().strftime('%Y-%m-%d_%H-%M')}.xlsx"

    # Respuesta
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


