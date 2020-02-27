
import decimal, math

def getAtPrecision(d, exp, normalize=True):
    '''Returns decimal to specified exponent.
    '''
    if d == d.to_integral():
        return x.quantize(decimal.Decimal('1'))
    d1 = d.quantize(exp)
    # rounded value might now be integral
    if normalize:
        return d1.quantize(decimal.Decimal('1')) if d1 == d1.to_integral() else d1.normalize()
    else:
        return d1

def Roundto2(x):
    if x < (math.pow(10, decimal.Decimal('-5')) - 5.0 * math.pow(10, decimal.Decimal('-7'))):
        return decimal.Decimal("0.0")
    else:
        Log10 = decimal.Decimal(str(math.log(decimal.Decimal(x))/math.log(10)))
        expon = decimal.Decimal(str(math.modf(Log10)[1]))
        if Log10 < decimal.Decimal('0'): 
            expon -=  decimal.Decimal('1')
        return (getAtPrecision(decimal.Decimal(x)/decimal.Decimal(str(math.pow(10, expon))), decimal.Decimal('.1')) * decimal.Decimal(str(math.pow(10, expon)))).normalize()