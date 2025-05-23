from decimal import Decimal
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from .models import Parametro, Tipo, Instrumento
from . forms.instrumento_form import InstrumentoForm, InstrumentoUpdateForm, ParametroForm
from django.utils.timezone import now
from django.http import JsonResponse
import openpyxl
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.shortcuts import render
from django.http import HttpResponse

def user_is_admin(user):
    return user.is_authenticated and not user.groups.filter(name__in=["Invitado", "Técnico"]).exists()

@login_required(login_url='/login/')
@user_passes_test(user_is_admin, login_url='/login/')
def crear_instrumento(request):
    if request.method == 'POST':
        instrumento_form = InstrumentoForm(request.POST)

        if instrumento_form.is_valid():
            instrumento = instrumento_form.save(commit=False)

            if not instrumento.fecha_alta:
                instrumento.fecha_alta = now()
            instrumento.save()

            tipo_id = request.POST.get('id_tipo')
            tipo = Tipo.objects.get(id=tipo_id)
            instrumento.id_tipo = tipo
            instrumento.save()

            tipo_nombre = tipo.nombre_tipo

            if tipo_nombre in ["PIEZÓMETRO", "FREATÍMETRO"]:
                parametros = [
                    {"nombre_parametro": "cb", "valor": Decimal(request.POST.get("cb", "0"))},
                    {"nombre_parametro": "ci", "valor": Decimal(request.POST.get("ci", "0"))},
                    {"nombre_parametro": "angulo", "valor": Decimal(request.POST.get("angulo", "0"))},
                ]
            elif tipo_nombre == "AFORADOR PARSHALL":
                parametros = [
                    {"nombre_parametro": "k", "valor": Decimal(request.POST.get("k", "0"))},
                    {"nombre_parametro": "u", "valor": Decimal(request.POST.get("u", "0"))},
                ]
            else:
                parametros = []

            for param in parametros:
                Parametro.objects.create(
                    id_instrumento=instrumento,
                    nombre_parametro=param["nombre_parametro"],
                    valor=param["valor"]
                )

            return JsonResponse({"success": True, "message": "✅ Instrumento guardado correctamente."})

        return JsonResponse({"success": False, "message": "❌ Error: Datos inválidos en el formulario."}, status=400)

    instrumento_form = InstrumentoForm()
    return render(request, "instrumento_form.html", {"instrumento_form": instrumento_form})

@login_required(login_url='/login/')
def instrumento_tabla(request):
    nombre_filtro = request.GET.get('nombre', '')
    tipo_filtro = request.GET.get('tipo', '')

    instrumentos = Instrumento.objects.all().prefetch_related('parametro_set')

    if nombre_filtro:
        instrumentos = instrumentos.filter(nombre__icontains=nombre_filtro)

    if tipo_filtro:
        instrumentos = instrumentos.filter(id_tipo__nombre_tipo=tipo_filtro)

    tipos_instrumento = Tipo.objects.values_list('nombre_tipo', flat=True).distinct()

    contexto = {
        'instrumentos': instrumentos,
        'tipos_instrumento': tipos_instrumento,
        'nombre_filtro': nombre_filtro,
        'tipo_filtro': tipo_filtro,
    }
    return render(request, 'instrumento_tabla.html', contexto)

@login_required(login_url='/login/')
@user_passes_test(user_is_admin, login_url='/login/')
def baja_instrumento(request, instrumento_id):
    if request.method == "POST":
        instrumento = get_object_or_404(Instrumento, id=instrumento_id)
        instrumento.activo = False  # Baja lógica
        instrumento.fecha_baja = now()
        instrumento.save()

        return JsonResponse({"success": True, "message": "✅ Instrumento dado de baja correctamente."})

    return JsonResponse({"success": False, "message": "❌ Error: Solicitud no válida."}, status=400)

@login_required(login_url='/login/')
@user_passes_test(user_is_admin, login_url='/login/')
def instrumento_modificar(request, instrumento_id):

    instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    ParametroFormSet = modelformset_factory(Parametro, form=ParametroForm, extra=0)

    if request.method == 'POST':
        form = InstrumentoUpdateForm(request.POST, instance=instrumento)
        formset = ParametroFormSet(request.POST, queryset=Parametro.objects.filter(id_instrumento=instrumento))

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return JsonResponse({"success": True, "message": "✅ Instrumento modificado correctamente."})

        return JsonResponse(
            {"success": False, "message": "❌ Error al modificar el instrumento. Verifica los datos ingresados."})

    form = InstrumentoUpdateForm(instance=instrumento)

    formset = ParametroFormSet(queryset=Parametro.objects.filter(id_instrumento=instrumento))

    return render(request, 'instrumento_modificar.html', {
        'form': form,
        'formset': formset,
        'instrumento': instrumento
    })

@login_required(login_url='/login/')
def export_instrumentos_excel(request):
    instrumentos = Instrumento.objects.prefetch_related("parametro_set").all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Instrumentos"

    headers = ["Nombre", "Tipo", "Fecha de Alta", "Fecha de Baja", "Activo", "Parámetros"]
    ws.append(headers)

    for instrumento in instrumentos:
        parametros = ", ".join(
            f"{parametro.nombre_parametro}={parametro.valor}"
            for parametro in instrumento.parametro_set.all()
        ) or "-"

        ws.append([
            instrumento.nombre,
            instrumento.id_tipo.nombre_tipo,
            instrumento.fecha_alta.strftime("%d/%m/%Y") if instrumento.fecha_alta else "-",
            instrumento.fecha_baja.strftime("%d/%m/%Y") if instrumento.fecha_baja else "-",
            "Sí" if instrumento.activo else "No",
            parametros
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="instrumentos.xlsx"'
    wb.save(response)
    return response

@login_required(login_url='/login/')
def export_instrumentos_pdf(request):
    instrumentos = Instrumento.objects.prefetch_related("parametro_set").all()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="instrumentos.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, "Lista de Instrumentos")

    data = [["Nombre", "Tipo", "Fecha de Alta", "Fecha de Baja", "Activo", "Parámetros"]]

    for instrumento in instrumentos:
        parametros = ", ".join(
            f"{parametro.nombre_parametro}={parametro.valor}"
            for parametro in instrumento.parametro_set.all()
        ) or "-"

        data.append([
            instrumento.nombre,
            instrumento.id_tipo.nombre_tipo,
            instrumento.fecha_alta.strftime("%d/%m/%Y") if instrumento.fecha_alta else "-",
            instrumento.fecha_baja.strftime("%d/%m/%Y") if instrumento.fecha_baja else "-",
            "Sí" if instrumento.activo else "No",
            parametros
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 100 - (len(data) * 20))

    p.showPage()
    p.save()
    return response