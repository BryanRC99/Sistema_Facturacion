from datetime import timedelta
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncDate, TruncHour
from django.utils.timezone import localdate

from facturacion_app.models import Factura


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
