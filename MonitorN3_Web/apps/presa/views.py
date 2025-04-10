from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/login/')
def generalidades(request):
    return render(request, 'generalidades.html')

@login_required(login_url='/login/')
def descripcion(request):
    return render(request, 'descripcion.html')

@login_required(login_url='/login/')
def dispositivos(request):
    return render(request, 'dispositivos.html')
