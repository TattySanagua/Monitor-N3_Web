from django.urls import path
from . import views

urlpatterns = [
    path('predefinidos/', views.predefinidos, name="predefinidos"),
    path('predefinidos/grafico', views.generar_grafico_predefinido, name="predefinidos_grafico"),
    path('personalizados/', views.personalizados, name='personalizados'),
    path('personalizado/grafico', views.generar_grafico, name='generar_grafico')
]