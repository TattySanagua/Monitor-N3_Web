from django import template

register = template.Library()

@register.filter
def key(dictionary, key_name):
    """Permite acceder a un diccionario con una clave dinámica en las plantillas."""
    if isinstance(dictionary, dict):
        return dictionary.get(key_name, {})
    return {}