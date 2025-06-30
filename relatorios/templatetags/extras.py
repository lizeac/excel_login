# seu_app/templatetags/extras.py

from django import template

register = template.Library()

@register.filter
def index(lista, i):
    try:
        return lista[i]
    except:
        return ''