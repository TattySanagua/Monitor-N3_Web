from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',  views.index, name="index"),
    path('usuario/', include('apps.usuario.urls')),
    path('embalse/', include('apps.embalse.urls')),
    path('precipitacion/', include('apps.precipitacion.urls')),
    path('instrumento/', include('apps.instrumento.urls')),
    path('medicion/', include('apps.medicion.urls')),
    path('graficos/', include('apps.graficos.urls')),
]
