from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Q
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
from django.templatetags.static import static
import os
from django.shortcuts import get_object_or_404
import json

from clientes.models import Cliente
from productos.models import Producto
from .models import Factura, DetalleFactura

# ============================
# IMPRIMIR FACTURA
# ============================

# ============================
# IMPRIMIR FACTURA
# ============================

def imprimir_factura(request, id):
    factura = get_object_or_404(Factura, id=id)

    # Proteger impresión
    if factura.estado != "ACTIVA":
        return render(
            request,
            "facturacion/factura_bloqueada.html",
            {
                "factura": factura
            },
            status=403
        )

    # Logo con ruta absoluta (WeasyPrint lo necesita)
    logo_url = request.build_absolute_uri(static("img/logo.png"))

    # Empresa
    empresa = {
        "nombre": "SuperMarket",
        "ruc": "99999999999999",
        "direccion": "Quito, Av Reinoso Rueda y Calle 8",
        "telefono": "0993395049",
        "correo": "contacto@empresa.com",
    }

    # Detalles
    detalles = factura.detalles.all()

    html_string = render_to_string(
        "facturacion/factura_pdf.html",
        {
            "factura": factura,
            "detalles": detalles,
            "empresa": empresa,
            "logo_url": logo_url,
        }
    )

    html = HTML(
        string=html_string,
        base_url=request.build_absolute_uri()
    )

    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="factura_{factura.id}.pdf"'
    )

    return response



# ============================
# LISTAR FACTURAS
# ============================
def lista_facturas(request):
    facturas = Factura.objects.all().order_by('-fecha')
    return render(request, 'facturacion/lista.html', {'facturas': facturas})


# ============================
# CREAR FACTURA
# ============================
@transaction.atomic
def crear_factura(request):
    clientes = Cliente.objects.all()
    productos = Producto.objects.filter(estado=True)

    if request.method == 'POST':
        cliente_id = request.POST['cliente']
        forma_pago = request.POST['forma_pago']

        # Crear número de factura simple (puedes mejorar)
        ultimo = Factura.objects.all().count() + 1
        numero_factura = f"001-001-{ultimo:09d}"

        factura = Factura.objects.create(
            cliente_id=cliente_id,
            forma_pago=forma_pago,
            numero=numero_factura,
            fecha=now()
        )

        # VARIABLES DE CALCULO
        subtotal = 0
        subtotal_iva = 0
        subtotal_cero = 0
        descuento_total = 0
        iva_total = 0

        # RECIBIR DETALLES DEL FORM
        productos_ids = request.POST.getlist('producto_id')
        cantidades = request.POST.getlist('cantidad')
        precios = request.POST.getlist('precio_unitario')
        descuentos = request.POST.getlist('descuento')

        for i in range(len(productos_ids)):
            prod = Producto.objects.get(id=productos_ids[i])
            cantidad = int(cantidades[i])
            precio = float(precios[i])
            desc = float(descuentos[i])

            sub = (precio * cantidad) - desc

            # Guardar detalle
            DetalleFactura.objects.create(
                factura=factura,
                producto=prod,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=desc,
                subtotal=sub
            )

            # ACTUALIZAR STOCK
            prod.stock -= cantidad
            prod.save()

            # CÁLCULOS TOTALES
            descuento_total += desc
            subtotal += sub

            if prod.iva:
                subtotal_iva += sub
            else:
                subtotal_cero += sub

        iva_total = subtotal_iva * 0.12
        total = subtotal + iva_total

        # Guardar totales en factura
        factura.subtotal = subtotal
        factura.subtotal_iva = subtotal_iva
        factura.subtotal_cero = subtotal_cero
        factura.descuento_total = descuento_total
        factura.iva_total = iva_total
        factura.total = total
        factura.save()

        return redirect('factura_lista')

    return render(request, 'facturacion/crear.html', {
        'clientes': clientes,
        'productos': productos
    })


# ============================
# VER FACTURA
# ============================
def ver_factura(request, id):
    factura = get_object_or_404(Factura, id=id)
    detalles = DetalleFactura.objects.filter(factura=factura)

    return render(request, 'facturacion/ver.html', {
        'factura': factura,
        'detalles': detalles
    })


# ============================
# ANULAR FACTURA
# ============================
@transaction.atomic
def anular_factura(request, id):
    factura = get_object_or_404(Factura, id=id)

    if factura.estado == "ANULADA":
        return redirect('factura_lista')

    # devolver stock
    for det in factura.detalles.all():
        prod = det.producto
        prod.stock += det.cantidad
        prod.save()

    factura.estado = "ANULADA"
    factura.save()

    return redirect('factura_lista')

# ============================
# AJAX: Buscar Producto
# ============================
def buscar_producto(request):
    query = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(codigo__icontains=query),
        estado=True
    )[:10]  # limitar resultados

    data = [
        {
            'id': p.id,
            'codigo': p.codigo,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'iva': p.iva,
            'stock': p.stock
        }
        for p in productos
    ]

    return JsonResponse({'resultados': data})


# ============================
# AJAX: Información del Cliente
# ============================
def cliente_info(request, id):
    try:
        c = Cliente.objects.get(id=id)
        data = {
            'id': c.id,
            'identificacion': c.identificacion,
            'nombre': c.nombre_razon_social,
            'telefono': c.telefono,
            'direccion': c.direccion,
            'correo': c.correo,
        }
        return JsonResponse(data)

    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)

