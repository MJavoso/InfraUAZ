from django import template

register = template.Library()

@register.simple_tag
def pagination_url(request, page_number):
    """Genera una URL de paginación manteniendo los parámetros de consulta existentes."""
    params = request.GET.copy()
    params['page'] = page_number
    return '?' + params.urlencode()