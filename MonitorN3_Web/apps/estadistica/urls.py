from django.urls import path
from . import views

urlpatterns = [
    path('resumen/', views.resumen_estadistico, name='resumen'),
    path('instrumentos/', views.mostrar_instrumentos, name='instrumento'),
    path('predicciones/', views.predicciones, name='predicciones'),

]