from django import template

register = template.Library()

@register.filter
def data_verbose(boundField):
    """
    Returns field's data or it's verbose version 
    for a field with choices defined.

    Usage::

        {% load data_verbose %}
        {{form.some_field|data_verbose}}
    """
    value = boundField.data or None
    if value is None:
        return '???'
    return dict(boundField.field.choices).get(value, '')
