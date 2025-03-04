from django.shortcuts import render

from django.shortcuts import render

def generalidades(request):
    return render(request, 'generalidades.html')

def descripcion(request):
    return render(request, 'descripcion.html')

def dispositivos(request):
    return render(request, 'dispositivos.html')
