from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.embalse_form, name="embalse_form"),
    path('nivelembalse/', views.nivelembalse, name='nivelembalse'),
    path('tabla/', views.embalse_precipitacion_tabla, name='embalse_precipitacion_tabla'),
    path('export/excel/', views.export_embalse_excel, name='export_embalse_excel'),
    path('export/pdf/', views.export_embalse_pdf, name='export_embalse_pdf'),
]