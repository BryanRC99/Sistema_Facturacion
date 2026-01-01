# auditoria/views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import AuditoriaLog

def dashboard(request):
    logs = AuditoriaLog.objects.all().order_by('-fecha')
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    auditorias = paginator.get_page(page)

    return render(request, "auditoria/dashboard.html", {
        "auditorias": auditorias
    })
