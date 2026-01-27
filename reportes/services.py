from datetime import timedelta
from decimal import Decimal
from django.db.models import DecimalField, IntegerField, F, Value, ExpressionWrapper

from django.apps import apps
from django.db.models import (
    Sum, Count, Avg, Max, F, Q, Value, DecimalField
)
from django.db.models.functions import (
    TruncDate, TruncHour, TruncWeek, TruncMonth, Coalesce
)
from django.utils.timezone import localdate

from facturacion_app.models import Factura


# ===================================================
# Helpers (modelos opcionales + utilidades)
# ===================================================
def _get_model(app_label: str, model_name: str):
    """
    Obtiene un modelo si existe; si no, retorna None.
    Esto permite que el services.py no reviente si aún no creaste
    DetalleFactura/Producto/Categoria, etc.
    """
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


def _date_filters(qs, fecha_inicio=None, fecha_fin=None, field="fecha"):
    """
    Aplica filtros por rango de fechas (por date) a un queryset.
    """
    if fecha_inicio:
        qs = qs.filter(**{f"{field}__date__gte": fecha_inicio})
    if fecha_fin:
        qs = qs.filter(**{f"{field}__date__lte": fecha_fin})
    return qs


def _trunc_by(group_by: str):
    """
    Agrupa por: 'dia' | 'semana' | 'mes'
    """
    group_by = (group_by or "dia").lower().strip()
    if group_by == "semana":
        return TruncWeek("fecha"), "periodo"
    if group_by == "mes":
        return TruncMonth("fecha"), "periodo"
    return TruncDate("fecha"), "periodo"


# ===================================================
# 📊 Ventas agrupadas por día (Gráfico principal)
# ===================================================
def ventas_por_dia(fecha_inicio=None, fecha_fin=None):
    queryset = Factura.objects.filter(estado='ACTIVA')

    if fecha_inicio:
        queryset = queryset.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(fecha__date__lte=fecha_fin)

    return (
        queryset
        .annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(
            total_vendido=Sum('total'),
            cantidad=Count('id')
        )
        .order_by('dia')
    )


# ===================================================
# 💳 Resumen COMPLETO del día (Cards principales)
# ===================================================
def resumen_ventas_hoy():
    hoy = localdate()

    data = Factura.objects.filter(
        estado='ACTIVA',
        fecha__date=hoy
    ).aggregate(
        total_vendido=Sum('total'),
        total_iva=Sum('iva_total'),
        subtotal_iva=Sum('subtotal_iva'),
        subtotal_cero=Sum('subtotal_cero'),
        descuentos=Sum('descuento_total'),
        cantidad_facturas=Count('id'),
        ticket_promedio=Avg('total')
    )

    return {
        'fecha': hoy,
        'total_vendido': data['total_vendido'] or 0,
        'total_iva': data['total_iva'] or 0,
        'subtotal_iva': data['subtotal_iva'] or 0,
        'subtotal_cero': data['subtotal_cero'] or 0,
        'descuentos': data['descuentos'] or 0,
        'cantidad_facturas': data['cantidad_facturas'] or 0,
        'ticket_promedio': data['ticket_promedio'] or 0,
    }


# ===================================================
# 📈 Comparación Hoy vs Ayer (con porcentaje)
# ===================================================
def comparacion_hoy_vs_ayer():
    hoy = localdate()
    ayer = hoy - timedelta(days=1)

    hoy_data = Factura.objects.filter(
        estado='ACTIVA', fecha__date=hoy
    ).aggregate(
        total=Sum('total'),
        cantidad=Count('id')
    )

    ayer_data = Factura.objects.filter(
        estado='ACTIVA', fecha__date=ayer
    ).aggregate(
        total=Sum('total'),
        cantidad=Count('id')
    )

    hoy_total = hoy_data['total'] or 0
    ayer_total = ayer_data['total'] or 0

    crecimiento = (
        ((hoy_total - ayer_total) / ayer_total) * 100
        if ayer_total > 0 else 0
    )

    return {
        'hoy_total': hoy_total,
        'ayer_total': ayer_total,
        'diferencia': hoy_total - ayer_total,
        'crecimiento_pct': crecimiento,
        'facturas_hoy': hoy_data['cantidad'],
        'facturas_ayer': ayer_data['cantidad'],
    }


# ===================================================
# ⏱️ Ventas por hora (Actividad del día)
# ===================================================
def ventas_por_hora_hoy():
    hoy = localdate()

    return (
        Factura.objects.filter(
            estado='ACTIVA',
            fecha__date=hoy
        )
        .annotate(hora=TruncHour('fecha'))
        .values('hora')
        .annotate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        .order_by('hora')
    )


# ===================================================
# 💳 Ventas por forma de pago (Donut)
# ===================================================
def ventas_por_forma_pago_hoy():
    hoy = localdate()

    return (
        Factura.objects.filter(
            estado='ACTIVA',
            fecha__date=hoy
        )
        .values('forma_pago')
        .annotate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        .order_by('-total')
    )


# ===================================================
# 🧾 Facturas del día (Tabla)
# ===================================================
def facturas_hoy():
    hoy = localdate()

    return Factura.objects.filter(
        estado='ACTIVA',
        fecha__date=hoy
    ).order_by('-fecha')


# ===================================================
# 🏆 Indicadores destacados del día
# ===================================================
def indicadores_destacados_hoy():
    hoy = localdate()

    return {
        'factura_mas_alta': Factura.objects.filter(
            estado='ACTIVA',
            fecha__date=hoy
        ).aggregate(max=Max('total'))['max'] or 0,

        'ultima_factura': Factura.objects.filter(
            estado='ACTIVA',
            fecha__date=hoy
        ).order_by('-fecha').first(),
    }


# ======================================================================
# ✅ NUEVO: Reporte por rango (día/semana/mes) + KPIs del rango
# ======================================================================
def ventas_por_rango(fecha_inicio=None, fecha_fin=None, group_by="dia"):
    """
    Para tu vista "Reporte de ventas": permite agrupar por día/semana/mes.
    Retorna filas: periodo, total_vendido, cantidad
    """
    qs = Factura.objects.filter(estado="ACTIVA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    trunc_fn, alias = _trunc_by(group_by)

    return (
        qs.annotate(**{alias: trunc_fn})
        .values(alias)
        .annotate(
            total_vendido=Coalesce(
                Sum("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad=Coalesce(
                Count("id"),
                Value(0, output_field=IntegerField())
            ),
        )
        .order_by(alias)
    )


def kpis_rango(fecha_inicio=None, fecha_fin=None):
    """
    KPIs para cards arriba del reporte por rango.
    """
    qs = Factura.objects.filter(estado="ACTIVA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    data = qs.aggregate(
        total_vendido=Coalesce(
            Sum("total"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        total_iva=Coalesce(
            Sum("iva_total"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        cantidad_facturas=Coalesce(
            Count("id"),
            Value(0, output_field=IntegerField())
        ),
        ticket_promedio=Coalesce(
            Avg("total"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        descuentos=Coalesce(
            Sum("descuento_total"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        subtotal_iva=Coalesce(
            Sum("subtotal_iva"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        subtotal_cero=Coalesce(
            Sum("subtotal_cero"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
    )

    # ✅ Ya viene todo tipado correctamente
    total_vendido = data["total_vendido"]
    cantidad_facturas = data["cantidad_facturas"]

    ticket_promedio = data["ticket_promedio"]
    if (ticket_promedio in (None, 0)) and cantidad_facturas > 0:
        # total_vendido es Decimal, cantidad_facturas es int → ok en Python
        ticket_promedio = total_vendido / cantidad_facturas

    return {
        "total_vendido": total_vendido,
        "total_iva": data["total_iva"],
        "cantidad_facturas": cantidad_facturas,
        "ticket_promedio": ticket_promedio or Decimal("0"),
        "descuentos": data["descuentos"],
        "subtotal_iva": data["subtotal_iva"],
        "subtotal_cero": data["subtotal_cero"],
    }


# ======================================================================
# ✅ NUEVO: Métodos de pago por rango
# ======================================================================
def ventas_por_forma_pago_rango(fecha_inicio=None, fecha_fin=None):
    qs = Factura.objects.filter(estado="ACTIVA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    return (
        qs.values("forma_pago")
        .annotate(
            total=Coalesce(
                Sum("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad=Coalesce(
                Count("id"),
                Value(0, output_field=IntegerField())
            ),
        )
        .order_by("-total")
    )


# ======================================================================
# ✅ NUEVO: Vendedores / usuarios (si tu Factura tiene FK user/vendedor)
# ======================================================================
def ventas_por_vendedor(fecha_inicio=None, fecha_fin=None):
    """
    Requiere que Factura tenga un campo FK: vendedor o user
    (ajusta el nombre del campo si es distinto).
    """
    qs = Factura.objects.filter(estado="ACTIVA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    if "vendedor" in [f.name for f in Factura._meta.fields]:
        field = "vendedor"
    elif "user" in [f.name for f in Factura._meta.fields]:
        field = "user"
    else:
        return Factura.objects.none().values("id")[:0]

    return (
        qs.values(f"{field}__id", f"{field}__username")
        .annotate(
            total=Coalesce(
                Sum("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad=Coalesce(
                Count("id"),
                Value(0, output_field=IntegerField())
            ),
            ticket_promedio=Coalesce(
                Avg("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
        )
        .order_by("-total")
    )


# ======================================================================
# ✅ NUEVO: Estados (ACTIVA / ANULADA) + reporte de anuladas
# ======================================================================
def facturas_por_estado(fecha_inicio=None, fecha_fin=None):
    qs = Factura.objects.all()
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    return (
        qs.values("estado")
        .annotate(
            total=Coalesce(
                Sum("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad=Coalesce(
                Count("id"),
                Value(0, output_field=IntegerField())
            ),
        )
        .order_by("-cantidad")
    )


def anuladas_rango(fecha_inicio=None, fecha_fin=None):
    qs = Factura.objects.filter(estado="ANULADA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    data = qs.aggregate(
        total_anulado=Coalesce(
            Sum("total"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
        ),
        cantidad_anuladas=Coalesce(
            Count("id"),
            Value(0, output_field=IntegerField())
        ),
    )

    return {
        "total_anulado": data["total_anulado"],
        "cantidad_anuladas": data["cantidad_anuladas"],
        "facturas": qs.order_by("-fecha"),
    }


# ======================================================================
# ✅ NUEVO: Clientes (Top clientes / frecuencia) si Factura tiene FK cliente
# ======================================================================
def top_clientes(fecha_inicio=None, fecha_fin=None, limit=20, q=None):
    """
    Requiere Factura.cliente (FK). Si no existe, retorna vacío.
    """
    if "cliente" not in [f.name for f in Factura._meta.fields]:
        return Factura.objects.none().values("id")[:0]

    qs = Factura.objects.filter(estado="ACTIVA")
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="fecha")

    if q:
        qs = qs.filter(
            Q(cliente__nombre__icontains=q) |
            Q(cliente__razon_social__icontains=q) |
            Q(cliente__identificacion__icontains=q)
        )

    rows = (
        qs.values("cliente_id", "cliente", "cliente__nombre_razon_social")
        
        .annotate(
            total=Coalesce(
                Sum("total"),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad_facturas=Coalesce(
                Count("id"),
                Value(0, output_field=IntegerField())
            ),
            ultima_compra=Max("fecha"),
        )
        .annotate(
            # ticket_promedio = total / cantidad_facturas (evita Avg sobre agregados)
            ticket_promedio=ExpressionWrapper(
                F("total") / Coalesce(
                    F("cantidad_facturas"),
                    Value(1, output_field=IntegerField())
                ),
                output_field=DecimalField(max_digits=14, decimal_places=2)
            )
        )
        .order_by("-total")[:limit]
    )

    return rows


# ======================================================================
# ✅ NUEVO: Productos / categorías / utilidad (si tienes DetalleFactura)
# ======================================================================
def _detalle_model():
    """
    Ajusta aquí si tu app/modelo se llaman distinto.
    - facturacion_app.DetalleFactura
    """
    return _get_model("facturacion_app", "DetalleFactura")


def top_productos(fecha_inicio=None, fecha_fin=None, limit=20, categoria_id=None, q=None):
    DetalleFactura = _detalle_model()
    if not DetalleFactura:
        return []

    detalle_fields = {f.name for f in DetalleFactura._meta.fields}

    factura_fk = "factura" if "factura" in detalle_fields else None
    producto_fk = "producto" if "producto" in detalle_fields else None
    cantidad_field = "cantidad" if "cantidad" in detalle_fields else None

    if not (factura_fk and producto_fk and cantidad_field):
        return []

    qs = DetalleFactura.objects.select_related(factura_fk, producto_fk).filter(
        **{f"{factura_fk}__estado": "ACTIVA"}
    )
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field=f"{factura_fk}__fecha")

    if categoria_id:
        qs = qs.filter(**{f"{producto_fk}__categoria_id": categoria_id})

    if q:
        qs = qs.filter(**{f"{producto_fk}__nombre__icontains": q})

    if "total" in detalle_fields:
        total_expr = F("total")
    elif "subtotal" in detalle_fields:
        total_expr = F("subtotal")
    elif "precio" in detalle_fields:
        total_expr = F("precio") * F(cantidad_field)
    else:
        total_expr = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    return (
        qs.values(f"{producto_fk}_id", f"{producto_fk}__nombre")
        .annotate(
            cantidad_vendida=Coalesce(Sum(cantidad_field), Value(0, output_field=IntegerField())),
            total_vendido=Coalesce(
                Sum(total_expr),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
        )
        .order_by("-total_vendido")[:limit]
    )


def ventas_por_categoria(fecha_inicio=None, fecha_fin=None, limit=30):
    DetalleFactura = _detalle_model()
    if not DetalleFactura:
        return []

    detalle_fields = {f.name for f in DetalleFactura._meta.fields}
    if "factura" not in detalle_fields or "producto" not in detalle_fields or "cantidad" not in detalle_fields:
        return []

    qs = DetalleFactura.objects.select_related("factura", "producto").filter(
        factura__estado="ACTIVA"
    )
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="factura__fecha")

    if "total" in detalle_fields:
        total_expr = F("total")
    elif "subtotal" in detalle_fields:
        total_expr = F("subtotal")
    elif "precio" in detalle_fields:
        total_expr = F("precio") * F("cantidad")
    else:
        total_expr = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    return (
        qs.values("producto__categoria_id", "producto__categoria__nombre")
        .annotate(
            total_vendido=Coalesce(
                Sum(total_expr),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            cantidad_items=Coalesce(Sum("cantidad"), Value(0, output_field=IntegerField())),
        )
        .order_by("-total_vendido")[:limit]
    )


def utilidad_por_rango(fecha_inicio=None, fecha_fin=None, limit=20, categoria_id=None):
    DetalleFactura = _detalle_model()
    if not DetalleFactura:
        return []

    detalle_fields = {f.name for f in DetalleFactura._meta.fields}
    if "factura" not in detalle_fields or "producto" not in detalle_fields or "cantidad" not in detalle_fields:
        return []

    qs = DetalleFactura.objects.select_related("factura", "producto").filter(
        factura__estado="ACTIVA"
    )
    qs = _date_filters(qs, fecha_inicio, fecha_fin, field="factura__fecha")

    if categoria_id:
        qs = qs.filter(producto__categoria_id=categoria_id)

    if "total" in detalle_fields:
        vendido_expr = F("total")
    elif "subtotal" in detalle_fields:
        vendido_expr = F("subtotal")
    elif "precio" in detalle_fields:
        vendido_expr = F("precio") * F("cantidad")
    else:
        vendido_expr = Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))

    if "costo" in detalle_fields:
        costo_unit_expr = F("costo")
    else:
        costo_unit_expr = F("producto__costo")

    costo_expr = costo_unit_expr * F("cantidad")

    rows = (
        qs.values("producto_id", "producto__nombre")
        .annotate(
            total_vendido=Coalesce(
                Sum(vendido_expr),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
            total_costo=Coalesce(
                Sum(costo_expr),
                Value(0, output_field=DecimalField(max_digits=14, decimal_places=2))
            ),
        )
        .annotate(
            utilidad=F("total_vendido") - F("total_costo"),
        )
        .order_by("-utilidad")[:limit]
    )

    out = []
    for r in rows:
        vendido = r["total_vendido"] or Decimal("0")
        utilidad = r["utilidad"] or Decimal("0")
        margen = (utilidad / vendido * 100) if vendido and vendido > 0 else Decimal("0")
        r["margen_pct"] = float(margen)
        out.append(r)

    return out

