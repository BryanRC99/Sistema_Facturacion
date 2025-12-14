from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Producto, Categoria
from proveedores.models import Proveedor

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
    productos = Producto.objects.all()  # Necesario para JS (validación en frontend)

    error = None
    form_data = {}  # ← Para mantener los valores ingresados

    if request.method == 'POST':

        # Guardamos TODOS los valores ingresados por si hay error
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

        # 🔥 Validación: código repetido
        if Producto.objects.filter(codigo=form_data['codigo']).exists():
            error = "El código ingresado ya existe. Por favor ingrese uno diferente."

        else:
            # Crear el producto
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
            )
            return redirect('lista_productos')

    return render(request, 'productos/crear.html', {
        'categorias': categorias,
        'proveedores': proveedores,
        'productos': productos,
        'error': error,
        'form_data': form_data,  # ← Muy importante
    })



def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        producto.codigo = request.POST.get('codigo', '').strip()
        producto.nombre = request.POST.get('nombre', '').strip()
        producto.categoria_id = request.POST.get('categoria')
        producto.proveedor_id = request.POST.get('proveedor')
        producto.precio = float(request.POST.get('precio', 0))
        producto.costo = float(request.POST.get('costo', 0))
        producto.stock = int(request.POST.get('stock', 0))
        producto.iva = True if request.POST.get('iva') == 'on' else False
        producto.descripcion = request.POST.get('descripcion', '').strip()
        producto.estado = True if request.POST.get('estado') == 'on' else False
        producto.save()
        return redirect('lista_productos')

    return render(request, 'productos/editar.html', {
        'producto': producto,
        'categorias': categorias,
        'proveedores': proveedores,
        'productos': productos,
        
    })


def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('lista_productos')
