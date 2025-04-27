from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.embalse_form, name="embalse_form"),
    path('nivelembalse/', views.nivelembalse, name='nivelembalse'),
    path('tabla/', views.embalse_precipitacion_tabla, name='embalse_precipitacion_tabla'),
    path('editar-embalse/<int:pk>/', views.editar_embalse, name='editar_embalse'),
    path('editar-precipitacion/<int:pk>/', views.editar_precipitacion, name='editar_precipitacion'),
    path('export/excel/', views.export_embalse_excel, name='export_embalse_excel'),
    path('export/pdf/', views.export_embalse_pdf, name='export_embalse_pdf'),
]