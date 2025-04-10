import pandas as pd
from reportlab.lib import colors
from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from django.db.models import Sum
from django.http import JsonResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from . forms.embalse_form import EmbalseForm
from . models import Embalse
from django.contrib.auth.decorators import login_required
from ..precipitacion.models import Precipitacion

@login_required(login_url='/login/')
def embalse_form(request):
    embalse_form = EmbalseForm()
    return render(request, 'embalse_form.html',  {'embalse_form': embalse_form})


def obtener_datos_embalse():
    embalses = pd.DataFrame.from_records(Embalse.objects.values("fecha", "nivel_embalse"))
    precipitaciones = pd.DataFrame.from_records(Precipitacion.objects.values("fecha", "valor"))

    embalses.rename(columns={"nivel_embalse": "Nivel Embalse [msnm]"}, inplace=True)
    precipitaciones.rename(columns={"valor": "Precipitación [mm]"}, inplace=True)

    df = pd.merge(embalses, precipitaciones, on="fecha", how="outer").fillna("-")
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%d-%m-%Y")

    df_final = df.sort_index(ascending=False)

    return df_final

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
def embalse_precipitacion_tabla(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

    embalses = Embalse.objects.values('fecha', 'nivel_embalse')
    embalse_dict = {e['fecha']: e['nivel_embalse'] for e in embalses}

    precipitaciones = Precipitacion.objects.values('fecha').annotate(total=Sum('valor'))
    precipitacion_dict = {p['fecha']: p['total'] for p in precipitaciones}

    todas_las_fechas = sorted(set(embalse_dict.keys()) | set(precipitacion_dict.keys()), reverse=True)

    if fecha_inicio and fecha_fin:
        todas_las_fechas = [f for f in todas_las_fechas if fecha_inicio <= f <= fecha_fin]

    datos_tabla = []
    for fecha in todas_las_fechas:
        datos_tabla.append({
            "fecha": fecha.strftime("%d-%m-%Y"),
            "nivel_embalse": embalse_dict.get(fecha, "-"),
            "precipitaciones": precipitacion_dict.get(fecha, "-"),
        })

    contexto = {
        "datos_tabla": datos_tabla,
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "",
        "fecha_fin": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "",
    }

    return render(request, "embalse_precipitacion_tabla.html", contexto)

@login_required(login_url='/login/')
def export_embalse_excel(request):
    df = obtener_datos_embalse()

    # Crear archivo Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="embalse_precipitaciones.xlsx"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Datos", index=False)

    return response

@login_required(login_url='/login/')
def export_embalse_pdf(request):
    df = obtener_datos_embalse()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="embalse_precipitaciones.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Reporte de Niveles de Embalse y Precipitaciones", styles["Title"])
    elements.append(title)

    # Convertir DataFrame a lista de listas para ReportLab
    tabla_data = [df.columns.tolist()] + df.values.tolist()

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