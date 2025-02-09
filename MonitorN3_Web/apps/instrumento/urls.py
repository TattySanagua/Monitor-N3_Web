from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_instrumento, name='crear'),
    path('tabla/', views.instrumento_tabla, name='instrumento_tabla'),
    path('dar_de_baja/<int:instrumento_id>/', views.baja_instrumento, name='baja_instrumento'),
    path('modificar/<int:instrumento_id>/', views.instrumento_modificar, name='instrumento_modificar'),
]