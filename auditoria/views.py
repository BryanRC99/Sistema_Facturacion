# auditoria/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import AuditoriaLog


def dashboard(request):
    logs = AuditoriaLog.objects.all().order_by('-fecha')

    q = request.GET.get('q', '')
    fecha = request.GET.get('fecha', '')
    usuario = request.GET.get('usuario', '')    

    if q:
        logs = logs.filter(
            Q(accion__icontains=q) |
            Q(modelo_afectado__icontains=q) |
            Q(usuario__username__icontains=q) |
            Q(registro_id__icontains=q)             # <-- CAMBIO AQUÍ
        )

    if fecha:
        logs = logs.filter(fecha__date=fecha)

    if usuario:
        logs = logs.filter(usuario__username__icontains=usuario)

    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    auditorias = paginator.get_page(page)

    params = request.GET.copy()
    params.pop('page', None)

    return render(request, "auditoria/dashboard.html", {
        "auditorias": auditorias,
        "params": params.urlencode(),
    })
