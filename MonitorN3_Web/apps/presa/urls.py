from django.urls import path
from . import views

urlpatterns = [
    path('generalidades/', views.generalidades, name='generalidades'),
    path('descripcion/', views.descripcion, name='descripcion'),
    path('dispositivos/', views.dispositivos, name='dispositivos'),
]