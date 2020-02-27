
import decimal

from django import template

from fallout.calculator.templatetags import Roundto2, getAtPrecision

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def roundoff_people(numtoround):
    if numtoround < 0.5:
        return "fewer than 1"
    else:
        return str(getAtPrecision(decimal.Decimal(numtoround), decimal.Decimal('1.')))

@register.filter
def roundoff_high(numtoround):
    if numtoround > 999.5:
        return "greater than 999"
    else:
        return str(getAtPrecision(decimal.Decimal(numtoround), decimal.Decimal('1.')))

@register.filter
def roundto2(data):
    try:
        return Roundto2(decimal.Decimal(data or '0.0'))
    except Exception as e:
        print(str(e))
        return '0'

@register.simple_tag
def thyroid_cancer_risk(total_future, baseline_future):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test3 = (getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        if test1 or test2 or test3:
            return getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1'))
    except Exception as e:
        print(str(e))
        return '0'

@register.simple_tag
def thyroid_cancer_risk_high_chances(total_future, baseline_future):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(baseline_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(baseline_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1')))
        test3 = (getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        if test1 or test2 or test3:
            return getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1'))
    except Exception as e:
        print(str(e))
        return '0'

@register.simple_tag
def thyroid_cancer_risk_low_chances(total_future, baseline_future, fail_precision):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test3 = (getAtPrecision(decimal.Decimal(baseline_future[2]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        if test1 or test2 or test3:
            return getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal(fail_precision))
    except Exception as e:
        print(str(e))
        return '0'
  
@register.simple_tag
def thyroid_cancer_risk_from_today_lower(total_future):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        if test1 or test2:
            return getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1'))
    except Exception as e:
        print(str(e))
        return '0'
    
@register.simple_tag
def thyroid_cancer_risk_from_today_upper(total_future):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        if test1 or test2:
            return getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1'))
    except Exception as e:
        print(str(e))
        return '0'
    
@register.simple_tag
def thyroid_cancer_risk_from_today_lower2(total_future):
    try:
        mult = decimal.Decimal('1000')
        test1 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test2 = (getAtPrecision(decimal.Decimal(total_future[3]) * mult, decimal.Decimal('1')) == getAtPrecision(decimal.Decimal(total_future[2]) * mult, decimal.Decimal('1')))
        test3 = (getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1')) == decimal.Decimal('0'))
        if test1 or test2 or test3:
            return getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('.1'), normalize=False)
        else:
            return getAtPrecision(decimal.Decimal(total_future[0]) * mult, decimal.Decimal('1'))
    except Exception as e:
        print(str(e))
        return '0'
