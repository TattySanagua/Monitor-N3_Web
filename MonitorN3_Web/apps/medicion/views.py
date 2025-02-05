import json, math
from django.shortcuts import render, redirect
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from .forms.medicion_form import MedicionPiezometroForm, MedicionFreatimetroForm, MedicionAforadorVolumetrico, MedicionAforadorParshall
from ..instrumento.models import Parametro

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
                nivel_freatico = cb - ((-math.cos(math.radians(angulo))) * lectura)
                return JsonResponse({'nivel_freatico': round(nivel_freatico, 2)})
            else:
                return JsonResponse({'error': 'Parámetros no encontrados'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
    elif request.method == 'GET':
        medicion_freatimetro_form = MedicionFreatimetroForm()
        return render(request, 'medicion_freatimetro_form.html', {'medicion_freatimetro_form': medicion_freatimetro_form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)

def freatimetro_guardar(request):
    if request.method == 'POST':
        form = MedicionFreatimetroForm(request.POST)
        if form.is_valid():
            medicion = form.save(commit=False)
            medicion.valor = request.POST.get('nivel_freatico')  # Obtener el valor del campo oculto
            medicion.save()
            return redirect('freatimetro_calcular')
        else:
            return render(request, 'medicion_freatimetro_form.html', {'medicion_freatimetro_form': form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)

def afovolumetrico_calcular(request):
    if request.method == 'POST':
        form = MedicionAforadorVolumetrico(request.POST)
        if form.is_valid():
            # Obtener los datos de volumen y tiempo
            v1, t1 = form.cleaned_data['volumen_1'], form.cleaned_data['tiempo_1']
            v2, t2 = form.cleaned_data['volumen_2'], form.cleaned_data['tiempo_2']
            v3, t3 = form.cleaned_data['volumen_3'], form.cleaned_data['tiempo_3']

            # Cálculo de caudales individuales (Q = V / T)
            q1 = v1 / t1 if t1 > 0 else 0
            q2 = v2 / t2 if t2 > 0 else 0
            q3 = v3 / t3 if t3 > 0 else 0

            # Cálculo del caudal promedio
            q_promedio = (q1 + q2 + q3) / 3

            # Devolver los resultados al frontend
            return JsonResponse({
                'q1': round(q1, 2),
                'q2': round(q2, 2),
                'q3': round(q3, 2),
                'q_promedio': round(q_promedio, 2)
            })
        else:
            return JsonResponse({'error': 'Formulario no válido'}, status=400)
    else:
        form = MedicionAforadorVolumetrico()
    return render(request, 'medicion_afovolumetrico_form.html', {'medicion_afovolumetrico_form': form})

def afovolumetrico_guardar(request):
    if request.method == 'POST':
        form = MedicionAforadorVolumetrico(request.POST)
        if form.is_valid():
            medicion = form.save(commit=False)
            q_promedio = request.POST.get('q_promedio')

            print(f"Caudal Promedio recibido: {q_promedio}")  # Verificamos el valor recibido

            try:
                medicion.valor = Decimal(q_promedio)
                medicion.save()
                return redirect('afovolumetrico_calcular')
            except (InvalidOperation, TypeError):
                return JsonResponse({'error': 'El caudal promedio debe ser un número válido.'}, status=400)

        else:
            return render(request, 'medicion_afovolumetrico_form.html', {'medicion_afovolumetrico_form': form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)

def afoparshall_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura_ha = data.get('lectura_ha')

            # Validación de los datos recibidos
            if not id_instrumento or lectura_ha is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            lectura_ha = float(lectura_ha)

            # Traer los parámetros k y u de la base de datos para el aforador seleccionado
            k_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='k').first()
            u_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='u').first()

            if k_param and u_param:
                k = float(k_param.valor)
                u = float(u_param.valor)

                # Cálculo del caudal: Q = k * ha^u
                caudal = k * math.pow(lectura_ha, u)

                return JsonResponse({'caudal': round(caudal, 3)})
            else:
                return JsonResponse({'error': 'Parámetros k y/u no encontrados para este aforador.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
    else:
        form = MedicionAforadorParshall()
        return render(request, 'medicion_afoparshall_form.html', {'medicion_aforador_parshall_form': form})

def afoparshall_guardar(request):
    if request.method == 'POST':
        form = MedicionAforadorParshall(request.POST)
        if form.is_valid():
            medicion = form.save(commit=False)

            caudal_calculado = request.POST.get('caudal_calculado')

            if caudal_calculado:
                medicion.valor = caudal_calculado
                medicion.save()
                messages.success(request, 'Medición guardada exitosamente.')
                return redirect('afoparshall_calcular')
            else:
                return JsonResponse({'error': 'El caudal calculado no fue encontrado.'}, status=400)
        else:
            return render(request, 'medicion_afoparshall_form.html', {'form': form})
    else:
        return JsonResponse({'error': 'Solicitud no válida'}, status=400)