import json, math
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from .forms.medicion_form import MedicionPiezometroForm, MedicionFreatimetroForm, MedicionAforadorVolumetrico, MedicionAforadorParshall
from ..instrumento.models import Parametro, Instrumento
from ..embalse.models import Embalse
from .models import Medicion
import openpyxl
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

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

def piezometro_tabla(request):
    # Obtener todos los instrumentos tipo PIEZÓMETRO
    piezometros = Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")

    # Obtener todas las mediciones de piezómetros y embalse, ordenadas por fecha
    mediciones = Medicion.objects.filter(id_instrumento__in=piezometros).order_by('-fecha')
    niveles_embalse = Embalse.objects.all().order_by('-fecha')

    # Estructura para almacenar los datos
    datos_tabla = {}

    # Agregar las mediciones de nivel de embalse
    for nivel in niveles_embalse:
        fecha = nivel.fecha.strftime("%d-%m-%Y")  # Formato de fecha
        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": nivel.nivel_embalse}  # Guardamos el nivel del embalse

    # Agregar las mediciones piezométricas
    for medicion in mediciones:
        fecha = medicion.fecha.strftime("%d-%m-%Y")
        instrumento = medicion.id_instrumento.nombre
        valor = medicion.valor

        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": "-"}

        datos_tabla[fecha][instrumento] = valor  # Guardamos la medición del piezómetro

    # Convertir los datos en listas para enviarlos al template
    fechas = sorted(datos_tabla.keys(), reverse=True)
    nombres_piezometros = [p.nombre for p in piezometros]

    contexto = {
        "fechas": fechas,
        "nombres_piezometros": nombres_piezometros,
        "datos_tabla": datos_tabla,
    }

    return render(request, "piezometro_tabla.html", contexto)

def freatimetro_tabla(request):
    # Obtener todos los instrumentos tipo FREATÍMETRO
    freatimetros = Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")

    # Obtener todas las mediciones de freatímetros y embalse, ordenadas por fecha
    mediciones = Medicion.objects.filter(id_instrumento__in=freatimetros).order_by('-fecha')
    niveles_embalse = Embalse.objects.all().order_by('-fecha')

    # Estructura para almacenar los datos
    datos_tabla = {}

    # Agregar las mediciones de nivel de embalse
    for nivel in niveles_embalse:
        fecha = nivel.fecha.strftime("%d-%m-%Y")
        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": nivel.nivel_embalse}

    # Agregar las mediciones de freatímetros
    for medicion in mediciones:
        fecha = medicion.fecha.strftime("%d-%m-%Y")
        instrumento = medicion.id_instrumento.nombre
        valor = medicion.valor

        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": "-"}

        datos_tabla[fecha][instrumento] = valor

    # Convertir los datos en listas para enviarlos al template
    fechas = sorted(datos_tabla.keys(), reverse=True)
    nombres_freatimetros = [f.nombre for f in freatimetros]

    contexto = {
        "fechas": fechas,
        "nombres_freatimetros": nombres_freatimetros,
        "datos_tabla": datos_tabla,
    }

    return render(request, "freatimetro_tabla.html", contexto)

def aforador_tabla(request):
    # Obtener todos los instrumentos tipo AFORADOR
    aforadores = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR")

    # Obtener todas las mediciones de aforadores y embalse, ordenadas por fecha
    mediciones = Medicion.objects.filter(id_instrumento__in=aforadores).order_by('-fecha')
    niveles_embalse = Embalse.objects.all().order_by('-fecha')

    # Estructura para almacenar los datos
    datos_tabla = {}

    # Agregar las mediciones de nivel de embalse
    for nivel in niveles_embalse:
        fecha = nivel.fecha.strftime("%d-%m-%Y")
        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": nivel.nivel_embalse}

    # Agregar las mediciones de aforadores
    for medicion in mediciones:
        fecha = medicion.fecha.strftime("%d-%m-%Y")
        instrumento = medicion.id_instrumento.nombre
        valor = medicion.valor

        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": "-"}

        datos_tabla[fecha][instrumento] = valor

    # Convertir los datos en listas para enviarlos al template
    fechas = sorted(datos_tabla.keys(), reverse=True)
    nombres_aforadores = [a.nombre for a in aforadores]

    contexto = {
        "fechas": fechas,
        "nombres_aforadores": nombres_aforadores,
        "datos_tabla": datos_tabla,
    }

    return render(request, "aforador_tabla.html", contexto)

def export_instrumento_excel(request, instrumentos, filename, sheet_title):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title

    mediciones = Medicion.objects.filter(id_instrumento__in=instrumentos).order_by('-fecha')
    niveles_embalse = Embalse.objects.all().order_by('-fecha')

    datos_tabla = {}

    for nivel in niveles_embalse:
        fecha = nivel.fecha.strftime("%d-%m-%Y")
        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": nivel.nivel_embalse}

    for medicion in mediciones:
        fecha = medicion.fecha.strftime("%d-%m-%Y")
        instrumento = medicion.id_instrumento.nombre
        valor = medicion.valor

        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": "-"}

        datos_tabla[fecha][instrumento] = valor

    fechas = sorted(datos_tabla.keys(), reverse=True)
    nombres_instrumentos = [p.nombre for p in instrumentos]

    ws.append(["Fecha", "Nivel Embalse"] + nombres_instrumentos)

    for fecha in fechas:
        row = [fecha, datos_tabla.get(fecha, {}).get("nivel_embalse", "-")]
        for nombre in nombres_instrumentos:
            row.append(datos_tabla.get(fecha, {}).get(nombre, "-"))
        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response

def export_piezometro_excel(request):
    piezometros = Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")
    return export_instrumento_excel(request, piezometros, "piezometro_mediciones.xlsx", "Piezómetros")

def export_freatimetro_excel(request):
    freatimetros = Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")
    return export_instrumento_excel(request, freatimetros, "freatimetro_mediciones.xlsx", "Freatímetros")

def export_aforador_excel(request):
    aforadores = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR")  # Trae todos los aforadores
    return export_instrumento_excel(request, aforadores, "aforador_mediciones.xlsx", "Aforadores")


def export_instrumento_pdf(request, instrumentos, filename, titulo):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Crear PDF en modo horizontal
    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, f"{titulo} - Mediciones")

    # Obtener las mediciones y estructurar los datos
    mediciones = Medicion.objects.filter(id_instrumento__in=instrumentos).order_by('-fecha')
    niveles_embalse = Embalse.objects.all().order_by('-fecha')

    # Crear estructura de datos para la tabla
    datos_tabla = {}
    for nivel in niveles_embalse:
        fecha = nivel.fecha.strftime("%d-%m-%Y")
        datos_tabla[fecha] = {"nivel_embalse": nivel.nivel_embalse}

    for medicion in mediciones:
        fecha = medicion.fecha.strftime("%d-%m-%Y")
        instrumento = medicion.id_instrumento.nombre
        valor = medicion.valor

        if fecha not in datos_tabla:
            datos_tabla[fecha] = {"nivel_embalse": "-"}

        datos_tabla[fecha][instrumento] = valor

    # Definir encabezados
    fechas = sorted(datos_tabla.keys(), reverse=True)
    nombres_instrumentos = [i.nombre for i in instrumentos]

    tabla_data = [["Fecha", "Nivel Embalse [msnm]"] + nombres_instrumentos]

    for fecha in fechas:
        fila = [fecha, datos_tabla.get(fecha, {}).get("nivel_embalse", "-")]
        for nombre in nombres_instrumentos:
            fila.append(datos_tabla.get(fecha, {}).get(nombre, "-"))
        tabla_data.append(fila)

    # Dibujar tabla en PDF
    table = Table(tabla_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Ubicación de la tabla en el PDF
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 100 - (len(tabla_data) * 20))

    # Guardar y retornar el PDF
    p.showPage()
    p.save()
    return response

def export_piezometro_pdf(request):
    piezometros = Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")
    return export_instrumento_pdf(request, piezometros, "piezometro_mediciones.pdf", "Piezómetros")


def export_freatimetro_pdf(request):
    freatimetros = Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")
    return export_instrumento_pdf(request, freatimetros, "freatimetro_mediciones.pdf", "Freatímetros")

def export_aforador_pdf(request):
    aforadores = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR")  # Trae todos los aforadores
    return export_instrumento_pdf(request, aforadores, "aforador_mediciones.pdf", "Aforadores")