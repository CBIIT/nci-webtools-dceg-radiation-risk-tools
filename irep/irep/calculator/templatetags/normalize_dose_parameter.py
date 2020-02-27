import math, decimal

from django import template

register = template.Library()

def Numpart(x):
    expon = decimal.Decimal('0')
    if x != decimal.Decimal('0'):
        Log10 = decimal.Decimal(str(math.log(x)/math.log(10)))
        expon = decimal.Decimal(str(math.modf(Log10)[1]))
        if Log10 < decimal.Decimal('0'): expon -=  decimal.Decimal('1')
    val = x/decimal.Decimal(str(math.pow(10, expon)))       
    return val.quantize(decimal.Decimal('.001')).normalize()

def Exppart(x):
    expon = decimal.Decimal('0')
    if x != decimal.Decimal('0'):
        Log10 = decimal.Decimal(str(math.log(x)/math.log(10)))
        expon = decimal.Decimal(str(math.modf(Log10)[1]))
        if Log10 < decimal.Decimal('0'): expon -= decimal.Decimal('1')
    return expon.normalize();

def Smartround(x):
    if x == decimal.Decimal('0'):
        return x.normalize()
    elif x >= decimal.Decimal('0.001') and x < decimal.Decimal('0.01'):
        return x.quantize(decimal.Decimal('.00001')).normalize()
    elif x >= decimal.Decimal('0.01') and x < decimal.Decimal('0.1'):
        return x.quantize(decimal.Decimal('.0001')).normalize()
    elif x >= decimal.Decimal('0.1') and x < decimal.Decimal('1'):
        return x.quantize(decimal.Decimal('.001')).normalize()
    elif x >= decimal.Decimal('1') and x < decimal.Decimal('10'):
        return x.quantize(decimal.Decimal('.01')).normalize()
    elif x >= decimal.Decimal('10') and x < decimal.Decimal('100'):
        return x.quantize(decimal.Decimal('1')) if x == x.to_integral() else x.quantize(decimal.Decimal('.1')).normalize()
    else:        
        return x.normalize()

@register.filter
def normalize_dose_parameter(boundField):
    try:
        val = decimal.Decimal(boundField.data or '0')
        if val == decimal.Decimal('0'):
            return '0'
        elif val < decimal.Decimal('0.001') or val > decimal.Decimal('1000'):
            return str(Numpart(val).quantize(decimal.Decimal('.01'))) + 'E' + str(Exppart(val))
        elif val >= decimal.Decimal('0.001') and val <= decimal.Decimal('1000'):
            return str(Smartround(val))
        else:
            return str(val.normalize())
    except Exception as e:
        return val
    