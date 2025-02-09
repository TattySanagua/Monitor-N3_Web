from django.shortcuts import render
from django.utils.timezone import now

def index(request):
    return render(request, 'index.html')

def base_context(request):
    return {'time': now().timestamp()}