from django.urls import path
from . import views

urlpatterns = [
    path('piezometro/nueva', views.piezometro_calcular, name='piezometro_calcular'),
    path('piezometro/guardar', views.piezometro_guardar, name='piezometro_guardar'),
    path('piezometro/tabla', views.piezometro_tabla, name='piezometro_tabla'),
    path('modificar/<int:id>', views.editar_medicion, name='editar_medicion'),
    path('piezometro/export/excel', views.export_piezometro_excel, name='export_piezometro_excel'),
    path('piezometro/export/pdf', views.export_piezometro_pdf, name='export_piezometro_pdf'),
    path('freatimetro/nueva', views.freatimetro_calcular, name='freatimetro_calcular'),
    path('freatimetro/guardar', views.freatimetro_guardar, name='freatimetro_guardar'),
    path('freatimetro/tabla', views.freatimetro_tabla, name='freatimetro_tabla'),
    path('freatimetro/export/excel', views.export_freatimetro_excel, name='export_freatimetro_excel'),
    path('freatimetro/export/pdf', views.export_freatimetro_pdf, name='export_freatimetro_pdf'),
    path('afovolumetrico/nueva', views.afovolumetrico_calcular, name='afovolumetrico_calcular'),
    path('afovolumetrico/guardar', views.afovolumetrico_guardar, name='afovolumetrico_guardar'),
    path('afoparshall/nueva', views.afoparshall_calcular, name='afoparshall_calcular'),
    path('afoparshall/guardar', views.afoparshall_guardar, name='afoparshall_guardar'),
    path('aforador/tabla', views.aforador_tabla, name='aforador_tabla'),
    path('aforador/export/excel', views.export_aforador_excel, name='export_aforador_excel'),
    path('aforador/export/pdf', views.export_aforador_pdf, name='export_aforador_pdf'),
]