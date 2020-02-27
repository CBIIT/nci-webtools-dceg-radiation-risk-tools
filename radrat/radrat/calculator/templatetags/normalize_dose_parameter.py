import decimal
import logging

from django import template

from radrat.calculator.templatetags import Numpart, Exppart, Smartround, condition_small_values

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def smart_round(data):
    try:
        return condition_small_values(Smartround(decimal.Decimal(data or '0')))
    except Exception as e:
        logger.error('smart_round failed with error: {}'.format(str(e)))
        return '0'
    

@register.filter
def normalize_dose_parameter(boundField):
    try:
        val = decimal.Decimal(boundField.data or '0')
        if val == decimal.Decimal('0'):
            return '0'
        elif val < decimal.Decimal('0.001') or val > decimal.Decimal('1000'):
            #return unicode(Numpart(val).quantize(decimal.Decimal('.01'))) + u'E' + unicode(Exppart(val))
            return condition_small_values(Smartround(val))
        elif val >= decimal.Decimal('0.001') and val <= decimal.Decimal('1000'):
            return condition_small_values(Smartround(val))
        else:
            return condition_small_values(val.normalize())
    except Exception as e:
        logger.error('normalize_dose_parameter failed with error: {}'.format(str(e)))
        return val
    