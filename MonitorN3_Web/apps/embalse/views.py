from django.shortcuts import render
from . models import Embalse
from django.http import HttpResponse


def form(request):
    return render(request, 'form.html',  {})

def nivelembalse(request):
    if request.method == "POST":
        fecha = request.POST['fecha']
        hora = request.POST['hora']
        nivel_embalse = request.POST['nivel_embalse']

        Embalse.objects.create(
            fecha=fecha,
            hora=hora,
            nivel_embalse=nivel_embalse,
        )
        return render(request, 'success.html', {})

    return render(request, 'form.html')