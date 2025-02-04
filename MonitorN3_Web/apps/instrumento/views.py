from django.shortcuts import render, redirect
from .models import Parametro, Tipo
from . forms.instrumento_form import InstrumentoForm
from django.utils.timezone import now
from django.http import HttpResponse

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