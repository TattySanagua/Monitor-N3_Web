from django.shortcuts import render
from django.utils import timezone

from . forms.precipitacion_form import PrecipitacionForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def precipitacion_form(request):
    precipitacion_form = PrecipitacionForm()
    return render(request, 'precipitacion_form.html', {'precipitacion_form': precipitacion_form})

@login_required(login_url='/login/')
def precipitacion(request):
    if request.method == "POST":
        precipitacion_form = PrecipitacionForm(request.POST)
        if precipitacion_form.is_valid():
            fecha = precipitacion_form.cleaned_data['fecha']
            hoy = timezone.now().date()

            if fecha > hoy:
                return JsonResponse({
                    "success": False,
                    "message": "⚠️ No se pueden registrar precipitaciones con fecha futura."
                })
            precipitacion_form.save()
            return JsonResponse({"success": True, "message": "✅ Precipitación guardada correctamente."})
        else:
            return JsonResponse(
                {"success": False, "message": "❌ Error al guardar la precipitación. Verifica los datos."})

    precipitacion_form = PrecipitacionForm()
    return render(request, "precipitacion_form.html", {"precipitacion_form": precipitacion_form})