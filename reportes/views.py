from django.shortcuts import render
from reportes.services import (
    ventas_por_dia,
    resumen_ventas_hoy,
    facturas_hoy,
    comparacion_hoy_vs_ayer
)


def dashboard(request):
    """
    Vista principal del dashboard de reportes
    """

    context = {
        'resumen': resumen_ventas_hoy(),
        'ventas_grafico': ventas_por_dia(),
        'facturas_hoy': facturas_hoy(),
        'comparacion': comparacion_hoy_vs_ayer(),
    }

    return render(request, 'reportes/dashboard.html', context)
