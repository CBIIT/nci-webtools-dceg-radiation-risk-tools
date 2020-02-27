
import decimal
import math
import logging

logger = logging.getLogger(__name__)

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

def getAtPrecision(d, exp):
    '''Returns decimal to specified exponent.
    '''
    if d == d.to_integral():
        return d.quantize(decimal.Decimal('1'))
    d1 = d.quantize(exp)
    # rounded value might now be integral
    return d1.quantize(decimal.Decimal('1')) if d1 == d1.to_integral() else d1.normalize()

def Smartround(x):
    if x < decimal.Decimal('0'):
        return '< 0'
    elif x == decimal.Decimal('0'):
        return x.normalize()
    elif x < decimal.Decimal('0.0001'):
        return x.quantize(decimal.Decimal('.0000001')).normalize()
    elif x >= decimal.Decimal('0.0001') and x < decimal.Decimal('0.001'):
        return x.quantize(decimal.Decimal('.000001')).normalize()
    elif x >= decimal.Decimal('0.001') and x < decimal.Decimal('0.01'):
        return x.quantize(decimal.Decimal('.00001')).normalize()
    elif x >= decimal.Decimal('0.01') and x < decimal.Decimal('0.1'):
        return x.quantize(decimal.Decimal('.0001')).normalize()
    elif x >= decimal.Decimal('0.1') and x < decimal.Decimal('1'):
        return x.quantize(decimal.Decimal('.001')).normalize()
    elif x >= decimal.Decimal('1') and x < decimal.Decimal('10'):
        return getAtPrecision(x, decimal.Decimal('.01'))
    elif x >= decimal.Decimal('10') and x < decimal.Decimal('100'):
        return getAtPrecision(x, decimal.Decimal('.1'))
    elif x >= decimal.Decimal('100') and x < decimal.Decimal('1000'):
        return x.quantize(decimal.Decimal('1'))
    elif x >= decimal.Decimal('1000') and x < decimal.Decimal('10000'):
        # return whole number with 1s place zeroed out  
        return x.quantize(decimal.Decimal('1')) if x == x.to_integral() else (x/decimal.Decimal('10')).quantize(decimal.Decimal('1')) * decimal.Decimal('10')
    elif x >= decimal.Decimal('10000') and x < decimal.Decimal('100000'):
        # return whole number with 1s and 10s places zeroed out  
        return x.quantize(decimal.Decimal('1')) if x == x.to_integral() else (x/decimal.Decimal('100')).quantize(decimal.Decimal('1')) * decimal.Decimal('100')
    elif x >= decimal.Decimal('100000'):
        return decimal.Decimal('100000')
    else:        
        return x.normalize()

def Smartround4(x):
    return x.quantize(decimal.Decimal('1')) if x == x.to_integral() else (x/decimal.Decimal('10')).quantize(decimal.Decimal('1')) * decimal.Decimal('10')
    
def Smartround5(x):
    return x.quantize(decimal.Decimal('1'))

def get_chances_10000(data):
    try:
        val = decimal.Decimal(data or '0')
        return val * decimal.Decimal('10000')
    except Exception as e:
        logger.error('get_chances_10000 failed with error: {}'.format(str(e)))
        return val

def get_chances_100000(data):
    try:
        val = decimal.Decimal(data or '0')
        return val * decimal.Decimal('100000')
    except Exception as e:
        logger.error('get_chances_100000 failed with error: {}'.format(str(e)))
        return val

def condition_small_values(val):
    '''special format for very small values'''
    if isinstance(val, decimal.Decimal) and val < decimal.Decimal('0.00001'):
        return  '{0:f}'.format(decimal.Decimal('%.1e' % val)) 
    return str(val)
             