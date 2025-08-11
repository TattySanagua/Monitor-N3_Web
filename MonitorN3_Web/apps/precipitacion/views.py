from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from . forms.precipitacion_form import PrecipitacionForm
from django.http import JsonResponse
from MonitorN3_Web.decorators import admin_o_tecnico

@login_required(login_url='/login/')
@admin_o_tecnico
def precipitacion_form(request):
    precipitacion_form = PrecipitacionForm()
    return render(request, 'precipitacion_form.html', {'precipitacion_form': precipitacion_form})

@login_required(login_url='/login/')
@admin_o_tecnico
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