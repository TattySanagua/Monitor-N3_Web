from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_views, name="login"),
    path("logout/", views.logout_views, name="logout"),
    path('',  views.login_views, name="inicio"),
    path('index/', views.index, name="index"),
    path('usuario/', include('apps.usuario.urls')),
    path('embalse/', include('apps.embalse.urls')),
    path('precipitacion/', include('apps.precipitacion.urls')),
    path('instrumento/', include('apps.instrumento.urls')),
    path('medicion/', include('apps.medicion.urls')),
    path('graficos/', include('apps.graficos.urls')),
    path('presa/', include('apps.presa.urls')),
    path('estadistica/', include('apps.estadistica.urls')),
]
