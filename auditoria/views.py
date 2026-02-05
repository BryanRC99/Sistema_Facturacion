# auditoria/views.py
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import AuditoriaLog
from usuarios.decorators import group_required


@group_required("SuperAdmin")
def dashboard(request):
    logs = AuditoriaLog.objects.select_related("usuario").all().order_by("-fecha")

    q = request.GET.get("q", "").strip()
    fecha = request.GET.get("fecha", "").strip()
    usuario = request.GET.get("usuario", "").strip()

    if q:
        filtros = (
            Q(accion__icontains=q) |
            Q(modelo_afectado__icontains=q) |
            Q(usuario__username__icontains=q) |
            Q(ip__icontains=q)
        )

        # Si q es número, permitir buscar por registro_id exacto
        if q.isdigit():
            filtros |= Q(registro_id=int(q))

        logs = logs.filter(filtros)

    if fecha:
        logs = logs.filter(fecha__date=fecha)

    if usuario:
        logs = logs.filter(usuario__username__icontains=usuario)

    paginator = Paginator(logs, 20)
    page = request.GET.get("page")
    auditorias = paginator.get_page(page)

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "auditoria/dashboard.html", {
        "auditorias": auditorias,
        "params": params.urlencode(),
    })
