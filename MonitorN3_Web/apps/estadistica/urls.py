from django.urls import path
from . import views

urlpatterns = [
    path('resumen/', views.resumen_estadistico, name='resumen'),
    path('predicciones/', views.predicciones, name='predicciones'),
    path('correlaciones/', views.correlaciones, name='correlaciones'),
]