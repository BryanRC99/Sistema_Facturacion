import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import cloudinary.uploader
from django.core.exceptions import ValidationError
from .models import Producto, Categoria
from proveedores.models import Proveedor
from django.contrib import messages


def verificar_codigo(request):
    codigo = request.GET.get("codigo", "").strip().lower()
    existe = Producto.objects.filter(codigo__iexact=codigo).exists()
    return JsonResponse({"existe": existe})


def lista_productos(request):
    productos = Producto.objects.all().select_related('categoria')
    return render(request, 'productos/lista.html', {'productos': productos})

def crear_producto(request):
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.filter(estado=True)
    productos = Producto.objects.all()

    error = None
    form_data = {}

    if request.method == 'POST':
        form_data = {
            'codigo': request.POST.get('codigo', '').strip(),
            'nombre': request.POST.get('nombre', '').strip(),
            'categoria': request.POST.get('categoria'),
            'proveedor': request.POST.get('proveedor'),
            'precio': request.POST.get('precio'),
            'costo': request.POST.get('costo'),
            'stock': request.POST.get('stock'),
            'iva': request.POST.get('iva') == 'on',
            'estado': request.POST.get('estado') == 'on',
            'descripcion': request.POST.get('descripcion', '').strip(),
        }

        imagen = request.FILES.get('imagen')

        if Producto.objects.filter(codigo=form_data['codigo']).exists():
            error = "El código ingresado ya existe. Por favor ingrese uno diferente."

        elif imagen:
            formatos_permitidos = ('image/jpeg', 'image/png', 'image/webp')
            max_size = 2 * 1024 * 1024

            if imagen.content_type not in formatos_permitidos:
                error = "Formato de imagen no permitido. Use JPG, PNG o WEBP."
            elif imagen.size > max_size:
                error = "La imagen no debe superar los 2MB."

        if not error:
            Producto.objects.create(
                codigo=form_data['codigo'],
                nombre=form_data['nombre'],
                categoria_id=form_data['categoria'],
                proveedor_id=form_data['proveedor'] or None,
                precio=float(form_data['precio']),
                costo=float(form_data['costo']),
                stock=int(form_data['stock']),
                iva=form_data['iva'],
                descripcion=form_data['descripcion'],
                estado=form_data['estado'],
                imagen=imagen if imagen else None
            )
            messages.success(request, "Producto guardado correctamente.")
            return redirect('lista_productos')

        # Si hubo error (validación), lo mostramos como toast también
        messages.error(request, f"❌ {error}")

    return render(request, 'productos/crear.html', {
        'categorias': categorias,
        'proveedores': proveedores,
        'productos': productos,
        'error': error,          # (puedes dejarlo por si lo usas en el template)
        'form_data': form_data,
    })


def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        producto.codigo = request.POST.get('codigo', '').strip()
        producto.nombre = request.POST.get('nombre', '').strip()
        producto.categoria_id = request.POST.get('categoria')
        producto.proveedor_id = request.POST.get('proveedor') or None
        producto.precio = float(request.POST.get('precio', 0) or 0)
        producto.costo = float(request.POST.get('costo', 0) or 0)
        producto.stock = int(request.POST.get('stock', 0) or 0)
        producto.iva = request.POST.get('iva') == 'on'
        producto.descripcion = request.POST.get('descripcion', '').strip()
        producto.estado = request.POST.get('estado') == 'on'

        # ===============================
        # MANEJO DE IMAGEN CLOUDINARY
        # ===============================
        imagen_nueva = request.FILES.get('imagen')

        if imagen_nueva:
            # 🔥 BORRAR IMAGEN ANTERIOR DE CLOUDINARY
            if producto.imagen:
                try:
                    cloudinary.uploader.destroy(producto.imagen.public_id)
                except Exception as e:
                    print(f"Error borrando imagen Cloudinary: {e}")
                    messages.warning(
                        request,
                        "⚠️ Se actualizó el producto, pero no se pudo borrar la imagen anterior."
                    )

            # Asignar nueva imagen
            producto.imagen = imagen_nueva

        producto.save()
        messages.success(request, "Producto actualizado correctamente.")
        return redirect('lista_productos')

    return render(request, 'productos/editar.html', {
        'producto': producto,
        'categorias': categorias,
        'proveedores': proveedores,
    })


def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if producto.imagen:
        try:
            cloudinary.uploader.destroy(producto.imagen.public_id)
        except Exception as e:
            print(f"Error borrando imagen Cloudinary: {e}")
            messages.warning(request, "⚠️ Producto eliminado, pero no se pudo borrar la imagen en Cloudinary.")

    producto.delete()
    messages.success(request, "Producto eliminado correctamente.")
    return redirect('lista_productos')
