from django.shortcuts import render
from . forms.precipitacion_form import PrecipitacionForm
from django.http import JsonResponse


def precipitacion_form(request):
    precipitacion_form = PrecipitacionForm()
    return render(request, 'precipitacion_form.html', {'precipitacion_form': precipitacion_form})

def precipitacion(request):
    if request.method == "POST":
        precipitacion_form = PrecipitacionForm(request.POST)
        if precipitacion_form.is_valid():
            precipitacion_form.save()
            return JsonResponse({"success": True, "message": "✅ Precipitación guardada correctamente."})
        else:
            return JsonResponse(
                {"success": False, "message": "❌ Error al guardar la precipitación. Verifica los datos."})

    precipitacion_form = PrecipitacionForm()
    return render(request, "precipitacion_form.html", {"precipitacion_form": precipitacion_form})