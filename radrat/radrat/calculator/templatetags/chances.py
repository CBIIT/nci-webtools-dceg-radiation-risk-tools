import decimal
import logging

from django import template

logger = logging.getLogger(__name__)
register = template.Library()

from radrat.calculator.templatetags import get_chances_10000, get_chances_100000

@register.filter
def chances_10000(data):
    """
    Returns field's data or it's verbose version 
    for a field with choices defined.

    Usage::

        {% load chances %}
        {{form.some_field|chances_10000}}
    """
    return get_chances_10000(data)

@register.filter
def chances_100000(data):
    """
    Returns field's data or it's verbose version 
    for a field with choices defined.

    Usage::

        {% load chances %}
        {{form.some_field|chances_100000}}
    """
    return get_chances_100000(data)

@register.filter
def is_chances_100000(data):
    """
    Returns field's data or it's verbose version 
    for a field with choices defined.

    Usage::

        {% load chances %}
        {{form.some_field|is_chances_100000}}
    """
    try:
        val = get_chances_100000(data)
        return val >= decimal.Decimal('100000')
    except Exception as e:
        logger.error('is_chances_100000 failed with error: {}'.format(str(e)))
        return val
