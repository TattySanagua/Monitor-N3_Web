from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from .models import Parametro, Tipo, Instrumento
from . forms.instrumento_form import InstrumentoForm, InstrumentoUpdateForm, ParametroForm
from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse


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
                    {"nombre_parametro": "cb", "valor": request.POST.get("cb",0)},
                    {"nombre_parametro": "angulo", "valor": request.POST.get("angulo", 0)},
                ]
            elif tipo == "AFORADOR PARSHALL":
                parametros = [
                    {"nombre_parametro": "k", "valor": request.POST.get("k", 0)},
                    {"nombre_parametro": "u", "valor": request.POST.get("u", 0)},
                ]
            else:
                parametros = []

            for param in parametros:
                Parametro.objects.create(
                    id_instrumento=instrumento,
                    nombre_parametro=param["nombre_parametro"],
                    valor=param["valor"]
                )
            return HttpResponse("<h1>EXITO</h1>")
        else:
            print(instrumento_form.errors)
            return HttpResponse("<h1>Error en el formulario</h1>")
    else:
            instrumento_form = InstrumentoForm()

    return render(request, "instrumento_form.html", {"instrumento_form": instrumento_form})

def instrumento_tabla(request):

    instrumentos = Instrumento.objects.all().prefetch_related('parametro_set')

    contexto = {'instrumentos': instrumentos}
    return render(request, 'instrumento_tabla.html', contexto)

def baja_instrumento(request, instrumento_id):
    """Vista para dar de baja un instrumento (baja lógica)."""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)
    instrumento.activo = False  # Baja lógica
    instrumento.fecha_baja = now()  # Registrar fecha de baja
    instrumento.save()
    return JsonResponse({'status': 'ok', 'message': 'Instrumento dado de baja correctamente'})

def instrumento_modificar(request, instrumento_id):
    """Vista para modificar un instrumento (nombre, fecha de instalación y parámetros)"""
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    #Formset para manejar múltiples parámetros
    ParametroFormSet = modelformset_factory(Parametro, form=ParametroForm, extra=0)

    if request.method == 'POST':
        form = InstrumentoUpdateForm(request.POST, instance=instrumento)
        formset = ParametroFormSet(request.POST, queryset=Parametro.objects.filter(id_instrumento=instrumento))

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('instrumento_tabla')
    else:
        form = InstrumentoUpdateForm(instance=instrumento)
        formset = ParametroFormSet(queryset=Parametro.objects.filter(id_instrumento=instrumento))

    return render(request, 'instrumento_modificar.html', {
        'form': form,
        'formset': formset,
        'instrumento': instrumento
    })