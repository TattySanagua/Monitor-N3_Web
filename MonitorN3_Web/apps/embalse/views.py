from reportlab.lib import colors
import openpyxl
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import timedelta, datetime
from django.db.models import Sum
from django.http import JsonResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from . forms.embalse_form import EmbalseForm
from . models import Embalse
from ..precipitacion.models import Precipitacion

def embalse_form(request):
    embalse_form = EmbalseForm()
    return render(request, 'embalse_form.html',  {'embalse_form': embalse_form})

def nivelembalse(request):
    if request.method == "POST":
        embalse_form = EmbalseForm(request.POST)
        if embalse_form.is_valid():
            embalse_form.save()
            return JsonResponse({"success": True, "message": "✅ Nivel de embalse guardado correctamente."})
        else:
            return JsonResponse(
                {"success": False, "message": "❌ Error al guardar el nivel de embalse. Verifica los datos."})

    embalse_form = EmbalseForm()
    return render(request, "embalse_form.html", {"embalse_form": embalse_form})

def embalse_precipitacion_tabla(request):

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

    fechas_embalse = Embalse.objects.values_list('fecha', flat=True).distinct()
    fechas_precipitacion = Precipitacion.objects.values_list('fecha', flat=True).distinct()

    todas_las_fechas = sorted(set(fechas_embalse) | set(fechas_precipitacion), reverse=True)

    if fecha_inicio and fecha_fin:
        todas_las_fechas = [f for f in todas_las_fechas if fecha_inicio <= f <= fecha_fin]

    datos_tabla = []
    for fecha in todas_las_fechas:
        nivel_embalse = Embalse.objects.filter(fecha=fecha).first()
        nivel_embalse_valor = nivel_embalse.nivel_embalse if nivel_embalse else "-"

        precipitaciones = {
            "del_dia": Precipitacion.objects.filter(fecha=fecha).aggregate(Sum('valor'))['valor__sum'] or "-",
            "tres_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=3)).aggregate(Sum('valor'))[
                             'valor__sum'] or "-",
            "cinco_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=5)).aggregate(Sum('valor'))[
                              'valor__sum'] or "-",
            "diez_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=10)).aggregate(Sum('valor'))[
                             'valor__sum'] or "-",
        }

        datos_tabla.append({
            "fecha": fecha.strftime("%d-%m-%Y"),
            "nivel_embalse": nivel_embalse_valor,
            "precipitaciones": precipitaciones,
        })

    contexto = {
        "datos_tabla": datos_tabla,
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "",
        "fecha_fin": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "",
    }

    return render(request, "embalse_precipitacion_tabla.html", contexto)

def export_embalse_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Embalse y Precipitaciones"

    headers = ["Fecha", "Nivel Embalse [msnm]", "Precipitación del Día", "3 Días Antes", "5 Días Antes", "10 Días Antes"]
    ws.append(headers)

    fechas_embalse = Embalse.objects.values_list('fecha', flat=True).distinct()
    fechas_precipitacion = Precipitacion.objects.values_list('fecha', flat=True).distinct()
    todas_las_fechas = sorted(set(fechas_embalse) | set(fechas_precipitacion), reverse=True)

    for fecha in todas_las_fechas:
        nivel_embalse = Embalse.objects.filter(fecha=fecha).first()
        nivel_embalse_valor = nivel_embalse.nivel_embalse if nivel_embalse else "-"

        precipitaciones = {
            "del_dia": Precipitacion.objects.filter(fecha=fecha).aggregate(Sum('valor'))['valor__sum'] or "-",
            "tres_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=3)).aggregate(Sum('valor'))['valor__sum'] or "-",
            "cinco_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=5)).aggregate(Sum('valor'))['valor__sum'] or "-",
            "diez_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=10)).aggregate(Sum('valor'))['valor__sum'] or "-",
        }

        ws.append([
            fecha.strftime("%d-%m-%Y"),
            nivel_embalse_valor,
            precipitaciones["del_dia"],
            precipitaciones["tres_dias"],
            precipitaciones["cinco_dias"],
            precipitaciones["diez_dias"],
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=embalse_precipitaciones.xlsx'
    wb.save(response)

    return response

def export_embalse_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="embalse_precipitaciones.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, "Reporte de Niveles de Embalse y Precipitaciones")

    fechas_embalse = Embalse.objects.values_list('fecha', flat=True).distinct()
    fechas_precipitacion = Precipitacion.objects.values_list('fecha', flat=True).distinct()
    todas_las_fechas = sorted(set(fechas_embalse) | set(fechas_precipitacion), reverse=True)

    tabla_data = [["Fecha", "Nivel Embalse [msnm]", "Precipitación del Día", "3 Días Antes", "5 Días Antes", "10 Días Antes"]]

    for fecha in todas_las_fechas:
        nivel_embalse = Embalse.objects.filter(fecha=fecha).first()
        nivel_embalse_valor = nivel_embalse.nivel_embalse if nivel_embalse else "-"

        precipitaciones = {
            "del_dia": Precipitacion.objects.filter(fecha=fecha).aggregate(Sum('valor'))['valor__sum'] or "-",
            "tres_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=3)).aggregate(Sum('valor'))['valor__sum'] or "-",
            "cinco_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=5)).aggregate(Sum('valor'))['valor__sum'] or "-",
            "diez_dias": Precipitacion.objects.filter(fecha=fecha - timedelta(days=10)).aggregate(Sum('valor'))['valor__sum'] or "-",
        }

        tabla_data.append([
            fecha.strftime("%d-%m-%Y"),
            nivel_embalse_valor,
            precipitaciones["del_dia"],
            precipitaciones["tres_dias"],
            precipitaciones["cinco_dias"],
            precipitaciones["diez_dias"],
        ])

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

    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 100 - (len(tabla_data) * 20))

    p.showPage()
    p.save()
    return response