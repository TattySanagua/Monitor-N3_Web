import json, math
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.utils import timezone
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from decimal import Decimal, InvalidOperation
from django.urls import reverse
from django.db import IntegrityError
from .forms.medicion_form import MedicionPiezometroForm, MedicionUpdateForm,MedicionFreatimetroForm, MedicionAforadorVolumetrico, MedicionAforadorParshall
from ..instrumento.models import Parametro, Instrumento
from ..embalse.models import Embalse
from .models import Medicion
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


def user_is_admin(user):
    return user.is_authenticated and not user.groups.filter(name__in=["Invitado", "Técnico"]).exists()

@login_required(login_url='/login/')
def piezometro_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura = data.get('lectura')

            if not id_instrumento or lectura is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            try:
                lectura = float(lectura)
            except ValueError:
                return JsonResponse({'error': 'Lectura debe ser un valor numérico'}, status=400)


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

@login_required(login_url='/login/')
def piezometro_guardar(request):
    if request.method == 'POST':
        form = MedicionPiezometroForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            instrumento = form.cleaned_data['id_instrumento']

            hoy = timezone.now().date()
            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ No se pueden registrar mediciones con fecha futura."
                })

            existe = Medicion.objects.filter(fecha=fecha, id_instrumento=instrumento).exists()

            if existe:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

            try:
                medicion = form.save(commit=False)
                medicion.valor = request.POST.get('nivel_piezometrico')
                medicion.save()
                return JsonResponse({
                    "success": True,
                    "message": "✅ Nivel piezométrico guardado correctamente."
                })
            except IntegrityError:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

        else:

            return JsonResponse({
                "success": False,
                "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada.",

            })

    return JsonResponse({
        "success": False,
        "message": "❌ Solicitud no válida."
    })


@login_required(login_url='/login/')
@user_passes_test(user_is_admin, login_url='/login/')
def editar_medicion(request, id):
    medicion = get_object_or_404(Medicion, id=id)

    if request.method == "POST":
        form = MedicionUpdateForm(request.POST, instance=medicion)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            hoy = timezone.now().date()

            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ No se puede asignar una fecha futura a la medición."
                })
            form.save()
            tipo = medicion.id_instrumento.id_tipo.nombre_tipo.upper()

            if "PIEZÓMETRO" in tipo:
                redirect_url = reverse('piezometro_tabla')
            elif "AFORADOR" in tipo:
                redirect_url = reverse('aforador_tabla')
            elif "FREATÍMETRO" in tipo:
                redirect_url = reverse('freatimetro_tabla')
            else:
                redirect_url = reverse('home')

            return JsonResponse({
                "success": True,
                "message": "✅ Instrumento modificado correctamente.",
                "redirect_url": redirect_url
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "❌ Error en el formulario."
            })

    else:
        form = MedicionUpdateForm(instance=medicion)

    instrumento = medicion.id_instrumento.nombre
    tipo = medicion.id_instrumento.id_tipo.nombre_tipo.upper()
    tipo_instrumento = (
        "piezometro" if "PIEZÓMETRO" in tipo else
        "aforador" if "AFORADOR" in tipo else
        "freatimetro"
    )

    return render(request, "medicion_modificar.html", {
        "form": form,
        "instrumento": instrumento,
        "tipo_instrumento": tipo_instrumento,
    })


@login_required(login_url='/login/')
def freatimetro_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura = data.get('lectura')

            if not id_instrumento or lectura is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            try:
                lectura = float(lectura)
            except ValueError:
                return JsonResponse({'error': 'Lectura debe ser un valor numérico'}, status=400)


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

@login_required(login_url='/login/')
def freatimetro_guardar(request):
    if request.method == 'POST':
        form = MedicionFreatimetroForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            instrumento = form.cleaned_data['id_instrumento']

            hoy = timezone.now().date()
            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ No se pueden registrar mediciones con fecha futura."
                })

            existe = Medicion.objects.filter(fecha=fecha, id_instrumento=instrumento).exists()

            if existe:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

            try:
                medicion = form.save(commit=False)
                medicion.valor = request.POST.get('nivel_freatico')
                medicion.save()
                return JsonResponse({
                    "success": True,
                    "message": "✅ Nivel freatico guardado correctamente."
                })
            except IntegrityError:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

        else:

            return JsonResponse({
                "success": False,
                "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada.",

            })

    return JsonResponse({
        "success": False,
        "message": "❌ Solicitud no válida."
    })

@login_required(login_url='/login/')
def afovolumetrico_calcular(request):
    if request.method == 'POST':
        form = MedicionAforadorVolumetrico(request.POST)
        if form.is_valid():
            v1, t1 = form.cleaned_data['volumen_1'], form.cleaned_data['tiempo_1']
            v2, t2 = form.cleaned_data['volumen_2'], form.cleaned_data['tiempo_2']
            v3, t3 = form.cleaned_data['volumen_3'], form.cleaned_data['tiempo_3']

            caudales = []
            resultados = {}

            for i, (v, t) in enumerate([(v1, t1), (v2, t2), (v3, t3)], start=1):
                if v is not None and t is not None:
                    if v < 0:
                        return JsonResponse({'error': f'El volumen #{i} no puede ser negativo.'}, status=400)
                    if t <= 0:
                        return JsonResponse({'error': f'El tiempo #{i} debe ser mayor a cero.'}, status=400)
                    q = v / t
                    caudales.append(q)
                    resultados[f'q{i}'] = round(q, 2)
                else:
                    resultados[f'q{i}'] = "Sin valor"

            if not caudales:
                return JsonResponse({'error': 'Debe ingresar al menos un par de volumen y tiempo válidos.'}, status=400)

            q_promedio = sum(caudales) / len(caudales)
            resultados['q_promedio'] = round(q_promedio, 2)

            return JsonResponse(resultados)
        else:
            return JsonResponse({'error': form.errors}, status=400)

    else:
        form = MedicionAforadorVolumetrico()
    return render(request, 'medicion_afovolumetrico_form.html', {'medicion_afovolumetrico_form': form})

@login_required(login_url='/login/')
def afovolumetrico_guardar(request):
    if request.method == 'POST':
        form = MedicionAforadorVolumetrico(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            instrumento = form.cleaned_data['id_instrumento']

            hoy = timezone.now().date()
            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "No se pueden registrar mediciones con fecha futura."
                })

            existe = Medicion.objects.filter(fecha=fecha, id_instrumento=instrumento).exists()

            if existe:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

            try:
                medicion = form.save(commit=False)
                medicion.valor = request.POST.get('q_promedio')
                medicion.save()
                return JsonResponse({
                    "success": True,
                    "message": "✅ Caudal guardado correctamente."
                })
            except IntegrityError:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })



        else:

            errores = form.errors.get('__all__')

            if getattr(errores, 'code', '') == 'unique_together':

                mensaje = "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."

            else:

                mensaje = "❌ Error: Datos inválidos en el formulario."

            return JsonResponse({

                "success": False,

                "message": mensaje

            })
    return JsonResponse({
        "success": False,
        "message": "❌ Solicitud no válida."
    })

@login_required(login_url='/login/')
def afoparshall_calcular(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            id_instrumento = data.get('id_instrumento')
            lectura_ha = data.get('lectura_ha')

            if not id_instrumento or lectura_ha is None:
                return JsonResponse({'error': 'Datos incompletos'}, status=400)

            try:
                lectura = float(lectura_ha)
            except ValueError:
                return JsonResponse({'error': 'Lectura debe ser un valor numérico'}, status=400)

            if lectura_ha < 0:
                return JsonResponse({'error': 'La lectura no puede ser un valor negativo'}, status=400)

            k_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='k').first()
            u_param = Parametro.objects.filter(id_instrumento=id_instrumento, nombre_parametro='u').first()

            if k_param and u_param:
                k = float(k_param.valor)
                u = float(u_param.valor)

                # Convertir lectura de cm a ha (en metros)
                ha = 0.259 + 0.035 - (lectura_ha / 100)

                if ha < 0:
                    return JsonResponse({'error': 'El valor de ha resultante es negativo. Verifica la lectura.'},
                                        status=400)

                # Calcular caudal en litros por segundo
                caudal = k * math.pow(ha, u) * 1000

                return JsonResponse({'caudal': round(caudal, 1)})
            else:
                return JsonResponse({'error': 'Parámetros k y/u no encontrados para este aforador.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al decodificar JSON'}, status=400)
    else:
        form = MedicionAforadorParshall()
        return render(request, 'medicion_afoparshall_form.html', {'medicion_aforador_parshall_form': form})

@login_required(login_url='/login/')
def afoparshall_guardar(request):
    if request.method == 'POST':
        form = MedicionAforadorParshall(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            instrumento = form.cleaned_data['id_instrumento']

            hoy = timezone.now().date()
            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ No se pueden registrar mediciones con fecha futura."
                })

            existe = Medicion.objects.filter(fecha=fecha, id_instrumento=instrumento).exists()

            if existe:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                })

            caudal_calculado = request.POST.get('caudal_calculado')
            if caudal_calculado:
                try:
                    medicion = form.save(commit=False)
                    medicion.valor = float(caudal_calculado)
                    medicion.save()
                    return JsonResponse({
                        "success": True,
                        "message": "✅ Caudal guardado correctamente."
                    })
                except ValueError:
                    return JsonResponse({
                        "success": False,
                        "message": "❌ Error: El caudal debe ser un número válido."
                    }, status=400)
                except IntegrityError:
                    return JsonResponse({
                        "success": False,
                        "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
                    })
            else:
                return JsonResponse({
                    "success": False,
                    "message": "❌ Error: No se encontró el caudal calculado."
                }, status=400)
        else:
            return JsonResponse({
                "success": False,
                "message": "⚠️ Ya existe una medición registrada para este instrumento en la fecha seleccionada."
            })

    return JsonResponse({
        "success": False,
        "message": "❌ Solicitud no válida."
    }, status=400)


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

    mediciones = Medicion.objects.filter(id_instrumento_id__in=df_instrumentos["id"], **filtros_mediciones).values("id",
        "fecha", "valor", "id_instrumento__nombre")
    df_mediciones = pd.DataFrame(list(mediciones))

    niveles_embalse = Embalse.objects.filter(**filtros_niveles).values("fecha", "nivel_embalse")
    df_embalse = pd.DataFrame(list(niveles_embalse))

    # Convertir fecha a formato `datetime`
    df_mediciones["fecha"] = pd.to_datetime(df_mediciones["fecha"])
    df_embalse["fecha"] = pd.to_datetime(df_embalse["fecha"])

    df_mediciones["dato"] = df_mediciones.apply(
        lambda row: {"valor": row["valor"], "id": row["id"]}, axis=1
    )

    # Pivotar usando esa nueva columna "dato"
    if not df_mediciones.empty:
        df_mediciones_pivot = df_mediciones.pivot_table(
            index="fecha",
            columns="id_instrumento__nombre",
            values="dato",
            aggfunc="first"
        )
    else:
        df_mediciones_pivot = pd.DataFrame()

    df_final = df_embalse.merge(df_mediciones_pivot, on="fecha", how="outer").sort_values("fecha", ascending=False)

    df_final["fecha"] = df_final["fecha"].dt.strftime("%d-%m-%Y")

    df_final = df_final.fillna("-")

    nombres = df_instrumentos["nombre"].tolist()
    filas_tabla = []

    for _, row in df_final.iterrows():
        fila = {
            "fecha": row["fecha"],
            "nivel_embalse": row.get("nivel_embalse", "-"),
            "valores": [row.get(nombre, "-") for nombre in nombres]
        }
        filas_tabla.append(fila)

    contexto = {
        "filas_tabla": filas_tabla,
        "nombres_aforadores" if tipo_instrumento == "AFORADOR" else "nombres_piezometros" if tipo_instrumento == "PIEZÓMETRO" else "nombres_freatimetros": nombres,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }

    return render(request, template, contexto)

@login_required(login_url='/login/')
def aforador_tabla(request):
    return obtener_datos_tabla("AFORADOR", "aforador_tabla.html", request)

@login_required(login_url='/login/')
def piezometro_tabla(request):
    return obtener_datos_tabla("PIEZÓMETRO", "piezometro_tabla.html", request)

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def export_instrumento_excel(request, instrumentos, filename, sheet_title):

    df = obtener_datos_instrumento(instrumentos)

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_title, index=True)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with open(filename, 'rb') as f:
        response.write(f.read())

    return response

@login_required(login_url='/login/')
def export_piezometro_excel(request):
    piezometros = Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")
    return export_instrumento_excel(request, piezometros, "piezometro_mediciones.xlsx", "Piezómetros")

@login_required(login_url='/login/')
def export_freatimetro_excel(request):
    freatimetros = Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")
    return export_instrumento_excel(request, freatimetros, "freatimetro_mediciones.xlsx", "Freatímetros")

@login_required(login_url='/login/')
def export_aforador_excel(request):
    aforadores = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR")  # Trae todos los aforadores
    return export_instrumento_excel(request, aforadores, "aforador_mediciones.xlsx", "Aforadores")

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def export_piezometro_pdf(request):
    piezometros = Instrumento.objects.filter(id_tipo__nombre_tipo="PIEZÓMETRO")
    return export_instrumento_pdf(request, piezometros, "piezometro_mediciones.pdf", "Piezómetros")

@login_required(login_url='/login/')
def export_freatimetro_pdf(request):
    freatimetros = Instrumento.objects.filter(id_tipo__nombre_tipo="FREATÍMETRO")
    return export_instrumento_pdf(request, freatimetros, "freatimetro_mediciones.pdf", "Freatímetros")

@login_required(login_url='/login/')
def export_aforador_pdf(request):
    aforadores = Instrumento.objects.filter(id_tipo__nombre_tipo__icontains="AFORADOR")  # Trae todos los aforadores
    return export_instrumento_pdf(request, aforadores, "aforador_mediciones.pdf", "Aforadores")