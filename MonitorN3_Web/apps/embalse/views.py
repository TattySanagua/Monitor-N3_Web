from django.shortcuts import render
from . forms.embalse_form import EmbalseForm

def embalse_form(request):
    embalse_form = EmbalseForm()
    return render(request, 'embalse_form.html',  {'embalse_form': embalse_form})

def nivelembalse(request):
    if request.method == "POST":
        embalse_form = EmbalseForm(request.POST)
        if embalse_form.is_valid():
            embalse_form.save()
        else:
            return render(request, 'embalse_form.html')

        return render(request, 'success.html', {})

    embalse_form = EmbalseForm()
    return render(request, 'embalse_form.html', {'embalse_form': embalse_form})

def tabla_embalse(request):
    pass