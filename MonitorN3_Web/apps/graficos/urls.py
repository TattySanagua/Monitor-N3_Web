from django.urls import path
from . import views

urlpatterns = [
    path('predefinidos/', views.predefinidos, name="predefinidos"),
    path('personalizados/', views.personalizados, name='personalizados'),
]