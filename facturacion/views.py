from django.shortcuts import render

def acceso_no_autorizado(request):
    return render(request, 'acceso_no_autorizado.html', status=401)
