from django.shortcuts import render
from django.utils.dateparse import parse_date

from reportes.services import (
    ventas_por_dia,
    resumen_ventas_hoy,
    comparacion_hoy_vs_ayer,
    facturas_hoy,

    # nuevos services
    ventas_por_rango,
    kpis_rango,
    ventas_por_forma_pago_rango,
    top_clientes,
    top_productos,
    ventas_por_categoria,
    anuladas_rango,
    ventas_por_vendedor,
    utilidad_por_rango,
)


def _get_dates(request):
    fecha_inicio = parse_date(request.GET.get("fecha_inicio") or "")
    fecha_fin = parse_date(request.GET.get("fecha_fin") or "")
    return fecha_inicio, fecha_fin


# =========================
# DASHBOARD (tu vista actual)
# =========================
def dashboard(request):
    contexto = {
        "resumen": resumen_ventas_hoy(),
        "comparacion": comparacion_hoy_vs_ayer(),
        "ventas_grafico": ventas_por_dia(),   # últimos días (sin rango)
        "facturas_hoy": facturas_hoy(),
    }
    return render(request, "reportes/dashboard.html", contexto)


# =========================
# 1) Ventas por rango
# =========================
def reporte_ventas_rango(request):
    fecha_inicio, fecha_fin = _get_dates(request)
    group_by = request.GET.get("group_by", "dia")

    contexto = {
        "fecha_inicio": fecha_inicio,   
        "fecha_fin": fecha_fin,
        "group_by": group_by,
        "kpis": kpis_rango(fecha_inicio, fecha_fin),
        "ventas": ventas_por_rango(fecha_inicio, fecha_fin, group_by=group_by),
    }
    return render(request, "reportes/reporte_ventas_rango.html", contexto)


# =========================
# 2) Métodos de pago
# =========================
def reporte_metodos_pago(request):
    fecha_inicio, fecha_fin = _get_dates(request)

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "metodos": ventas_por_forma_pago_rango(fecha_inicio, fecha_fin),
        "kpis": kpis_rango(fecha_inicio, fecha_fin),
    }
    return render(request, "reportes/reporte_metodos_pago.html", contexto)


# =========================
# 3) Clientes
# =========================
def reporte_clientes(request):
    fecha_inicio, fecha_fin = _get_dates(request)
    q = request.GET.get("q", "").strip()

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "q": q,
        "clientes": top_clientes(fecha_inicio, fecha_fin, limit=20, q=q) or [],
    }
    return render(request, "reportes/reporte_clientes.html", contexto)


# =========================
# 4) Productos
# =========================
def reporte_productos(request):
    fecha_inicio, fecha_fin = _get_dates(request)
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria_id") or None

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "q": q,
        "categoria_id": categoria_id,
        "productos": top_productos(
            fecha_inicio, fecha_fin, limit=20, categoria_id=categoria_id, q=q
        ) or [],
    }
    return render(request, "reportes/reporte_productos.html", contexto)


# =========================
# 5) Categorías
# =========================
def reporte_categorias(request):
    fecha_inicio, fecha_fin = _get_dates(request)

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "categorias": ventas_por_categoria(fecha_inicio, fecha_fin) or [],
    }
    return render(request, "reportes/reporte_categorias.html", contexto)


# =========================
# 6) Anuladas
# =========================
def reporte_anuladas(request):
    fecha_inicio, fecha_fin = _get_dates(request)
    data = anuladas_rango(fecha_inicio, fecha_fin)

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_anulado": data["total_anulado"],
        "cantidad_anuladas": data["cantidad_anuladas"],
        "facturas": data["facturas"],
    }
    return render(request, "reportes/reporte_anuladas.html", contexto)


# =========================
# 7) Vendedores
# =========================
def reporte_vendedores(request):
    fecha_inicio, fecha_fin = _get_dates(request)

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "vendedores": ventas_por_vendedor(fecha_inicio, fecha_fin),
    }
    return render(request, "reportes/reporte_vendedores.html", contexto)


# =========================
# 8) Utilidad
# =========================
def reporte_utilidad(request):
    fecha_inicio, fecha_fin = _get_dates(request)
    categoria_id = request.GET.get("categoria_id") or None

    contexto = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "categoria_id": categoria_id,
        "utilidad": utilidad_por_rango(fecha_inicio, fecha_fin, limit=20, categoria_id=categoria_id) or [],
    }
    return render(request, "reportes/reporte_utilidad.html", contexto)
