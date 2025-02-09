from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.precipitacion_form, name='precipitacion_form'),
    path('precipitacion/', views.precipitacion, name='precipitacion'),
]