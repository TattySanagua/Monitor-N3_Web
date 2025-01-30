from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.form, name='form'),
    path('precipitacion/', views.precipitacion, name='precipitacion'),
]