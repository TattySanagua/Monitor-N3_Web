import json

from django.shortcuts import render, redirect
from .models import Medicion
from .forms.medicion_form import MedicionPiezometroForm
from django.http import HttpResponse, JsonResponse
from ..instrumento.models import Parametro
import math

def piezometro_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura = data.get('lectura')

            if not id_instrumento or lectura is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            lectura = float(lectura)

            cb_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='CB').first()
            angulo_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='angulo').first()

            if cb_param and angulo_param:
                cb = float(cb_param.valor)
                angulo = float(angulo_param.valor)
                nivel_piezometrico = cb - ((-math.cos(math.radians(angulo))) * lectura)
                return JsonResponse({'nivel_piezometrico': round(nivel_piezometrico, 2)})
            else:
                return JsonResponse({'error': 'Parámetros no encontrados'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
    elif request.method == 'GET':
        medicion_piezometro_form = MedicionPiezometroForm()
        return render(request, 'medicion_piezometro_form.html', {'medicion_piezometro_form': medicion_piezometro_form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)

def piezometro_guardar(request):
    if request.method == 'POST':
        form = MedicionPiezometroForm(request.POST)
        if form.is_valid():
            medicion = form.save(commit=False)
            medicion.valor = request.POST.get('nivel_piezometrico')  # Obtener el valor del campo oculto
            medicion.save()
            return redirect('piezometro_calcular')
        else:
            return render(request, 'medicion_piezometro_form.html', {'medicion_piezometro_form': form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)



def freatimetro_calcular(request):
    pass

def afovolumetrico_calcular(request):
    pass

def afoparshall_calcular(request):
    pass

