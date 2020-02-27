from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def active_href(request, url_name):
    url = reverse(url_name)
    class_attr = 'active' if url == request.path else ''
    return mark_safe("class='%s' href='%s'" % (class_attr, url,))