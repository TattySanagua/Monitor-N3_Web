from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect

def es_admin(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()

def es_tecnico_o_admin(user):
    return user.is_authenticated and user.groups.filter(name__in=['Técnico', 'Administrador']).exists()

def es_invitado(user):
    return user.is_authenticated and user.groups.filter(name='Invitado').exists()


def solo_admin(view_func):
    decorator = user_passes_test(es_admin, login_url='/login/')
    return decorator(view_func)

def admin_o_tecnico(view_func):
    decorator = user_passes_test(es_tecnico_o_admin, login_url='/login/')
    return decorator(view_func)

def solo_invitado(view_func):
    decorator = user_passes_test(es_invitado, login_url='/login/')
    return decorator(view_func)