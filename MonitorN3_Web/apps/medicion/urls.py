from django.urls import path
from . import views

urlpatterns = [
    path('piezometro/nueva', views.piezometro_calcular, name='piezometro_calcular'),
    path('freatimetro/nueva', views.freatimetro_calcular, name='freatimetro_calcular'),
    path('afovolumetrico/nueva', views.afovolumetrico_calcular, name='afovolumetrico_calcular'),
    path('afoparshall/nueva', views.afoparshall_calcular, name='afoparshall_calcular'),
    path('piezometro/guardar', views.piezometro_guardar, name='piezometro_guardar'),
]