from django.urls import path
from . import views

urlpatterns = [
    path('resumen/', views.resumen_estadistico, name='resumen'),

]