from django.contrib.auth.models import Group

def roles_usuario(request):
    if not request.user.is_authenticated:
        return {
            'es_administrador': False,
            'es_tecnico': False,
            'es_invitado': False,
        }

    grupos = request.user.groups.values_list('name', flat=True)
    return {
        'es_administrador': 'Administrador' in grupos,
        'es_tecnico': 'Técnico' in grupos,
        'es_invitado': 'Invitado' in grupos,
    }