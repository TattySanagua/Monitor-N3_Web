from django.shortcuts import render
from . forms.precipitacion_form import PrecipitacionForm
from django.http import HttpResponse

def precipitacion_form(request):
    precipitacion_form = PrecipitacionForm()
    return render(request, 'precipitacion_form.html', {'precipitacion_form': precipitacion_form})

def precipitacion(request):
    if request.method == "POST":
        precipitacion_form = PrecipitacionForm(request.POST)
        if precipitacion_form.is_valid():
            precipitacion_form.save()
            return HttpResponse("<h1>EXITO</h1>")
        else:
            return HttpResponse("<h1>No se pudo guardar</h1>")


    return HttpResponse("<h1>No se pudo guardar</h1>")