from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.embalse_form, name="embalse_form"),
    path('nivelembalse/', views.nivelembalse, name='nivelembalse'),
    path('tablaembalse/', views.tabla_embalse, name='tabla_embalse')
]