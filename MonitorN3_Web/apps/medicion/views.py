import json, math
from datetime import datetime
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from decimal import Decimal, InvalidOperation
from .forms.medicion_form import MedicionPiezometroForm, MedicionFreatimetroForm, MedicionAforadorVolumetrico, MedicionAforadorParshall
from ..instrumento.models import Parametro, Instrumento
from ..embalse.models import Embalse
from .models import Medicion
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
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
            medicion.valor = request.POST.get('nivel_piezometrico')
            medicion.save()
            return JsonResponse({"success": True, "message": "✅ Nivel piezométrico guardado correctamente."})
        else:
            return JsonResponse({"success": False, "message": "❌ Error al guardar la medición. Verifica los datos."})

    return JsonResponse({"success": False, "message": "❌ Solicitud no válida."})


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
            nivel_freatico = request.POST.get('nivel_freatico')

            if nivel_freatico:
                try:
                    medicion.valor = float(nivel_freatico)
                    medicion.save()
                    return JsonResponse({"success": True, "message": "✅ Nivel freático guardado correctamente."})
                except ValueError:
                    return JsonResponse(
                        {"success": False, "message": "❌ Error: El nivel freático debe ser un número válido."},
                        status=400)
            else:
                return JsonResponse(
                    {"success": False, "message": "❌ Error: No se encontró el nivel freático calculado."}, status=400)
        else:
            return JsonResponse({"success": False, "message": "❌ Error: Datos inválidos en el formulario."}, status=400)

    return JsonResponse({"success": False, "message": "❌ Solicitud no válida."}, status=400)


def afovolumetrico_calcular(request):
    if request.method == 'POST':
        form = MedicionAforadorVolumetrico(request.POST)
        if form.is_valid():

            v1, t1 = form.cleaned_data['volumen_1'], form.cleaned_data['tiempo_1']
            v2, t2 = form.cleaned_data['volumen_2'], form.cleaned_data['tiempo_2']
            v3, t3 = form.cleaned_data['volumen_3'], form.cleaned_data['tiempo_3']

            q1 = v1 / t1 if t1 > 0 else 0
            q2 = v2 / t2 if t2 > 0 else 0
            q3 = v3 / t3 if t3 > 0 else 0

            q_promedio = (q1 + q2 + q3) / 3

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

            try:
                medicion.valor = Decimal(q_promedio)
                medicion.save()
                return JsonResponse({"success": True, "message": "✅ Caudal guardado correctamente."})
            except (InvalidOperation, TypeError):
                return JsonResponse(
                    {"success": False, "message": "❌ Error: El caudal promedio debe ser un número válido."}, status=400)
        else:
            return JsonResponse({"success": False, "message": "❌ Error: Datos inválidos en el formulario."}, status=400)

    return JsonResponse({"success": False, "message": "❌ Solicitud no válida."}, status=400)


def afoparshall_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura_ha = data.get('lectura_ha')

            if not id_instrumento or lectura_ha is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            lectura_ha = float(lectura_ha)

            k_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='k').first()
            u_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='u').first()

            if k_param and u_param:
                k = float(k_param.valor)
                u = float(u_param.valor)

                # Fórmula: Q = k * ha^u
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
                try:
                    medicion.valor = float(caudal_calculado)
                    medicion.save()
                    return JsonResponse({"success": True, "message": "✅ Caudal guardado correctamente."})
                except ValueError:
                    return JsonResponse({"success": False, "message": "❌ Error: El caudal debe ser un número válido."},
                                        status=400)
            else:
                return JsonResponse({"success": False, "message": "❌ Error: No se encontró el caudal calculado."},
                                    status=400)
        else:
            return JsonResponse({"success": False, "message": "❌ Error: Datos inválidos en el formulario."}, status=400)

    return JsonResponse({"success": False, "message": "❌ Solicitud no válida."}, status=400)


def obtener_datos_tabla(tipo_instrumento, template, request):
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    filtros_mediciones = {}
    filtros_niveles = {}

    if fecha_inicio:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        filtros_mediciones["fecha__gte"] = fecha_inicio_dt
        filtros_niveles["fecha__gte"] = fecha_inicio_dt

    if fecha_fin:
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        filtros_mediciones["fecha__lte"] = fecha_fin_dt
        filtros_niveles["fecha__lte"] = fecha_fin_dt

    instrumentos = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains=tipo_instrumento).values("id", "nombre")
    df_instrumentos = pd.DataFrame(list(instrumentos))

    mediciones = Medicion.objects.filter(id_instrumento_id__in=df_instrumentos["id"], **filtros_mediciones).values(
        "fecha", "valor", "id_instrumento__nombre")
    df_mediciones = pd.DataFrame(list(mediciones))

    niveles_embalse = Embalse.objects.filter(**filtros_niveles).values("fecha", "nivel_embalse")
    df_embalse = pd.DataFrame(list(niveles_embalse))

    # Convertir fecha a formato `datetime`
    df_mediciones["fecha"] = pd.to_datetime(df_mediciones["fecha"])
    df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])

    if not df_mediciones.empty:
        df_mediciones_pivot = df_mediciones.pivot_table(index="fecha", columns="id_instrumento__nombre", values="valor",
                                                        aggfunc="first")
    else:
        df_mediciones_pivot = pd.DataFrame()

    df_final = df_embalse.merge(df_mediciones_pivot, on="fecha", how="outer").sort_values("fecha", ascending=False)

    df_final["fecha"] = df_final["fecha"].dt.strftime("%d-%m-%Y")

    df_final = df_final.fillna("-")

    datos_tabla = df_final.set_index("fecha").to_dict(orient="index")

    contexto = {
        "fechas": df_final["fecha"].tolist(),
        "nombres_aforadores" if tipo_instrumento == "AFORADOR" else "nombres_piezometros" if tipo_instrumento == "PIEZÓMETRO" else "nombres_freatimetros":
            df_instrumentos["nombre"].tolist(),
        "datos_tabla": datos_tabla,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }

    return render(request, template, contexto)

def aforador_tabla(request):
    return obtener_datos_tabla("AFORADOR", "aforador_tabla.html", request)

def piezometro_tabla(request):
    return obtener_datos_tabla("PIEZÓMETRO", "piezometro_tabla.html", request)

def freatimetro_tabla(request):
    return obtener_datos_tabla("FREATÍMETRO", "freatimetro_tabla.html", request)


def obtener_datos_instrumento(instrumentos):

    mediciones = Medicion.objects.filter(id_instrumento__in=instrumentos).values(
        'fecha', 'id_instrumento__nombre', 'valor'
    ).order_by("fecha")

    niveles_embalse = Embalse.objects.values('fecha', 'nivel_embalse')

    df_mediciones = pd.DataFrame(list(mediciones))
    df_niveles = pd.DataFrame(list(niveles_embalse))

    df_mediciones['fecha'] = pd.to_datetime(df_mediciones['fecha'])
    df_niveles['fecha'] = pd.to_datetime(df_niveles['fecha'])

    df_mediciones = df_mediciones.pivot_table(
        index='fecha', columns='id_instrumento__nombre', values='valor', aggfunc='first'
    )

    df_niveles.set_index('fecha', inplace=True)
    df_final = df_niveles.join(df_mediciones, how='outer')

    df_final = df_final.fillna("-")

    df_final = df_final.sort_index(ascending=False)

    return df_final

def export_instrumento_excel(request, instrumentos, filename, sheet_title):

    df = obtener_datos_instrumento(instrumentos)

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_title, index=True)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with open(filename, 'rb') as f:
        response.write(f.read())

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
    df = obtener_datos_instrumento(instrumentos)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(titulo, styles["Title"])
    elements.append(title)

    df_reset = df.reset_index()

    tabla_data = [df_reset.columns.tolist()] + df_reset.fillna("-").values.tolist()

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

    elements.append(table)
    doc.build(elements)

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