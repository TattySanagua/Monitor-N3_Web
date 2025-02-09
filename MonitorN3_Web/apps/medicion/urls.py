from django.urls import path
from . import views

urlpatterns = [
    path('piezometro/nueva', views.piezometro_calcular, name='piezometro_calcular'),
    path('piezometro/guardar', views.piezometro_guardar, name='piezometro_guardar'),
    path('piezometro/tabla', views.piezometro_tabla, name='piezometro_tabla'),
    path('freatimetro/nueva', views.freatimetro_calcular, name='freatimetro_calcular'),
    path('freatimetro/guardar', views.freatimetro_guardar, name='freatimetro_guardar'),
    path('freatimetro/tabla', views.freatimetro_tabla, name='freatimetro_tabla'),
    path('afovolumetrico/nueva', views.afovolumetrico_calcular, name='afovolumetrico_calcular'),
    path('afovolumetrico/guardar', views.afovolumetrico_guardar, name='afovolumetrico_guardar'),
    path('afoparshall/nueva', views.afoparshall_calcular, name='afoparshall_calcular'),
    path('afoparshall/guardar', views.afoparshall_guardar, name='afoparshall_guardar'),
    path('aforador/tabla', views.aforador_tabla, name='aforador_tabla'),
]