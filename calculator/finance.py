import unittest
import logging

import locale
# for number formatting

import sympy
# for equation rearranging

global FORMULAS
FORMULAS = {}
# contains all the cached function rearrangements

RESULT_PRECISION = 4 # How many decimals should we round results from formulas to


def num_format(num):
    """Format a number using commas and 4 decimal places."""
    num = round(num, 4)
    return "{:,.4f}".format(num)


def all_functions(var, expr, vars):
    """Generates formulas to solve for as many variables in the given expression as the symply module can.
    Returns a list of lambdas for the rearrangements. Lambdas have the equation attribute containing the sympy.Equation.
    Also caches the sympy.Symbol objects given as vars inside 'symbols' dict element."""
    root_var = var
    root_expr = expr
    var = None
    expr = None
    functions = {}

    vars.sort(key=lambda v:v.name) # so we can predict the argument order
    root_eq = sympy.Eq(root_var, root_expr) # so we can rearrange it
    logging.debug("Given equation:", root_eq)
    #sympy.pprint(root_eq)
                  
    for var in vars:
        try:
            expr, = sympy.solve(root_eq, var)
        except NotImplementedError as e:
            print("No method found to solve for {} in equation".format(var))
            sympy.pprint(root_eq)
            continue
        if not expr:
            logging.warning("Couldn't solve for {}".format(var.name))
            continue
        eq = sympy.Eq(var, expr)
        logging.debug("Derived equation:", eq)
        #sympy.pprint(eq)

        new_vars = vars.copy()
        new_vars.remove(var)
        functions[var.name] = sympy.lambdify(new_vars, expr)

        # embed the equation for odd solving
        functions[var.name].equation = eq

    # embed the symbols for odd solving
    functions['symbols'] = {}
    for s in vars:
        functions['symbols'][str(s)] = s
        
    return functions    


# Time Value of Money
def tmv(pv=None, fv=None, r=None, n=None, should_round=True):
    """Converts between present money and future money taking into account interest rates and years past.
    pv: present value
    fv: future value with compound interest added
    r: compound yearly interest rate
    n: years
    """
    global FORMULAS
    name = 'solve'

    # generate all rearrangements of the given expression
    if name not in FORMULAS:
        _pv, _fv, _r, _n = sympy.symbols("pv fv r n")
        pv_expr = _fv / ((1+_r)**_n)
        FORMULAS[name] = all_functions(_pv, pv_expr, [_pv, _fv, _r, _n])

    # insist on the right number of arguments
    supplied = sum(1 if v is not None else 0 for v in (pv, fv, r, n))
    if supplied != 3:
        raise Exception("Invalid number of arguments")

    if pv is None:
        ret = [FORMULAS[name]['pv'](fv, n, r), "PV"]
    elif fv is None:
        ret = [FORMULAS[name]['fv'](n, pv, r), "FV"]
    elif r is None:
        ret = [FORMULAS[name]['r'](fv, n, pv), "r"]
    elif n is None:
        ret = [FORMULAS[name]['n'](fv, pv, r), "n"]
    else:
        print("You supplied all the arguments, there's nothing to calculate")
        return None

    if should_round:
        ret[0] = round(ret[0], RESULT_PRECISION)
    return ret
    

class Test_tmv(unittest.TestCase):
    def test_pv(self):
        pv, _ = tmv(fv=1000, r=0.02, n=10)
        self.assertAlmostEqual(pv, 820.3483)

    def test_fv(self):
        fv, _ = tmv(pv=1000, r=0.02, n=10)
        self.assertAlmostEqual(fv, 1218.9944)

    def test_r(self):
        r, _ = tmv(pv=1000, fv=1218.9944, n=10)
        self.assertAlmostEqual(r, 0.02)

    def test_n(self):
        n, _ = tmv(pv=1000, fv=1218.9944, r=0.02)
        self.assertAlmostEqual(n, 10)


def perpetuity(pv=None, C=None, r=None, should_round=True):
    """Calculates for perpetuities given the annual payment and the interest rate.
    pv: present value
    C: yearly payment
    r: yearly interest rate
    """
    global FORMULAS
    name = 'perpetuity'

    # generate all rearrangements of the given expression
    if name not in FORMULAS:
        pv_, C_, r_ = sympy.symbols("pv C r")
        pv_expr = C_ / r_
        FORMULAS[name] = all_functions(pv_, pv_expr, [pv_, C_, r_])

    # insist on the right number of arguments
    supplied = sum(1 if v is not None else 0 for v in (pv, C, r))
    if supplied != 2:
        raise Exception("Invalid number of arguments")

    if pv is None:
        ret = [FORMULAS[name]['pv'](C, r), "PV"]
    elif C is None:
        ret = [FORMULAS[name]['C'](pv, r), "C"]
    elif r is None:
        ret = [FORMULAS[name]['r'](C, pv), "r"]
    else:
        print("You supplied all the arguments, there's nothing to calculate")
        return None

    if should_round:
        ret[0] = round(ret[0], RESULT_PRECISION)
    return ret


class Test_perpetuity(unittest.TestCase):
    def test_pv(self):
        pv, _ = perpetuity(C=1000, r=0.02)
        self.assertAlmostEqual(pv, 50_000)

    def test_C(self):
        C, _ = perpetuity(pv=50_000, r=0.02)
        self.assertAlmostEqual(C, 1000)

    def test_r(self):
        r, _ = perpetuity(pv=50_000, C=1000)
        self.assertAlmostEqual(r, 0.02)


def _annuity_pv(pv=None, C=None, r=None, n=None, should_round=True):
    global FORMULAS
    name = 'annuity_pv'

    # generate all rearrangements of the given expression
    if name not in FORMULAS:
        _pv, _C, _r, _n = sympy.symbols("pv C r n")
        pv_expr = _C * 1/_r * (1 - 1/(1+_r)**_n)
        FORMULAS[name] = all_functions(_pv, pv_expr, [_pv, _C, _r, _n])
    # insist on the right number of arguments
    supplied = sum(1 if v is not None else 0 for v in (pv, C, r, n))
    if supplied != 3:
        raise Exception("Invalid number of arguments")


    if pv is None:
        ret = [FORMULAS[name]['pv'](C, n, r), "PV"]
    elif C is None:
        ret = [FORMULAS[name]['C'](n, pv, r), "C"]
    elif r is None:
        raise NotImplementedError("Can't calculate for r because I can't rearrange the formula.")
        print("Use the calculator with {}PV; {}C; {}N; CPT; I/Y".format(pv, C, n))
    elif n is None:
        raise NotImplementedError("Can't calculate for n because I can't rearrange the formula.")
        print("Use the calculator with {}PV; {}C; {}I/Y; CPT; N".format(pv, C, r))
    else:
        print("You supplied all the arguments, there's nothing to calculate")
        return None

    if should_round:
        ret[0] = round(ret[0], RESULT_PRECISION)
    return ret


class Test_annuity_pv(unittest.TestCase):
    def test_pv(self):
        pv, _ = _annuity_pv(C=1000, r=0.02, n=10)
        self.assertAlmostEqual(pv, 8982.5850)

    def test_C(self):
        C, _ = _annuity_pv(pv=8982.5850, r=0.02, n=10)
        self.assertAlmostEqual(C, 1000)


def _annuity_fv(fv=None, C=None, r=None, n=None, should_round=True):
    if fv is None:
        pv, _ = _annuity_pv(C=C, r=r, n=n, should_round=False)
        fv, _ = tmv(pv=pv, r=r, n=n, should_round=False)
        ret = [fv, "FV"]
    else:
        pv, _ = tmv(fv=fv, r=r, n=n, should_round=False)
        ret = _annuity_pv(pv=pv, C=C, r=r, n=n, should_round=False)

    if should_round:
        ret[0] = round(ret[0], RESULT_PRECISION)
    return ret


class Test_annuity_pv(unittest.TestCase):
    def test_fv(self):
        pv, _ = _annuity_fv(C=1000, r=0.02, n=10)
        self.assertAlmostEqual(pv, 10949.7210)

    def test_C(self):
        C, _ = _annuity_fv(fv=10949.7210, r=0.02, n=10)
        self.assertAlmostEqual(C, 1000)
        

# Time Value of Money
def annuity(pv=None, fv=None, C=None, r=None, n=None):
    """Converts between present money and future money taking into account interest rates and years past.
    pv: present value
    fv: future value with compound interest added
    r: compound periodly interest rate
    n: periods
    C: periodly payment
    """
    
    supplied = sum(1 if v is not None else 0 for v in (pv, fv, C, r, n))
    if supplied == 3:
        if pv is None:
            return _annuity_fv(fv=fv, C=C, r=r, n=n)
        elif fv is None:
            return _annuity_pv(pv=pv, C=C, r=r, n=n)
        else:
            print("No present or future value specified")
    elif supplied == 4:
        raise NotImplemented("Can't do this yet")
    

class Test_annuity(unittest.TestCase): pass
    # test from fv to pv
    # test from pv to fv
        

# Time Value of Money
def ytm(ytm=None, fv=None, cpn=None, n=None, p=None, should_round=True):
    """Converts between present money and future money taking into account interest rates and years past.
    ytm: Yield to maturity.
    fv: future value including coupon payments and payout.
    cpn: coupon payment amount in dollars.
    n: number of coupon payment periods.
    p: Current market price.
    """
    global FORMULAS
    name = 'ytm'

    # generate all rearrangements of the given expression
    if name not in FORMULAS:
        _ytm, _fv, _cpn, _p, _n = sympy.symbols("ytm fv cpn p n")
        p_expr = _cpn * (1/_ytm)*(1 - ( 1/(1+_ytm)**_n )) + (_fv/(1+_ytm)**_n)
        FORMULAS[name] = all_functions(_p, p_expr, [_ytm, _fv, _cpn, _n, _p])

    # insist on the right number of arguments
    supplied = sum(1 if v is not None else 0 for v in (ytm, fv, cpn, n, p))
    if supplied != 4:
        raise Exception("Invalid number of arguments")
    
    if ytm is None:
        ret = FORMULAS[name]['p'].equation.subs({'p': p, 'cpn':cpn, 'n':n, 'fv':fv})
        rets = []
        for i in range(1000):
            try:
<<<<<<< HEAD
=======
                # THIS LINE NEEDS To be changed. Essentially we are brute forcing the answer here using the rearranged formula.
>>>>>>> 1ed4fb9206856cd829f3f39546cf4f1083c1e2f0
                rets.append(sympy.nsolve(ret, sympy.Symbol("ytm"), (i+1)/1000))
            except ValueError: pass
            finally: pass
        logging.debug(rets)
        ret = [rets[0], "YTM"]
    elif fv is None:
        ret = [FORMULAS[name]['fv'](ytm=ytm, cpn=cpn, n=n, p=p), "FV"]
    elif cpn is None:
        print(FORMULAS[name]['cpn'].equation)
        ret = [FORMULAS[name]['cpn'](ytm=ytm, fv=fv, n=n, p=p), "CPN"]
    elif n is None:
        ret = [FORMULAS[name]['n'](ytm=ytm, fv=fv, cpn=cpn, p=p), "n"]
    elif p is None:
        ret = [FORMULAS[name]['p'](ytm=ytm, fv=fv, cpn=cpn, n=n), "P"]
    else:
        print("You supplied all the arguments, there's nothing to calculate")
        return None

    if should_round:
        ret[0] = round(ret[0], RESULT_PRECISION)
    return ret
    

class Test_ytm(unittest.TestCase):
    def test_ytm(self):
        ret = ytm(fv=1000, cpn=25, p=957.3490, n=10)
        self.assertEqual(ret[1], 'YTM')
        self.assertEqual(str(ret[0]), '0.0300')

    def test_fv(self):
        ret = ytm(cpn=25, p=957.3490, n=10, ytm=0.03)
        self.assertEqual(ret[1], 'FV')
        self.assertEqual(round(ret[0], 4), 1000.0000)

    def test_cpn(self):
        ret = ytm(fv=1000, p=957.3490, n=10, ytm=0.03)
        self.assertEqual(ret[1], 'CPN')
        self.assertEqual(round(ret[0], 4), 25.0000)

    # TODO test the other two function rearrangements

"""
Things still required

Variance of an investment:
  Var = 1/(T-1)((R_1-R_avg)^2+...+(R_T-R_avg)^2)
  Where T is the number of periods, R_1 is the return for period 1, R_avg is the average return for all periods.

Fix number format for large numbers

Price and YTM of a coupon bond with n coupon payments. So we need to be able to use annuity to
calculate PV and FV given four other arguments.

EAR interest, APR interest rate, Nominal rate
  EAR = 1  + (APR/m)**m - 1
  m is the compounding periods per year (monthly means m=12)

annuities with n years of odd deposit amounts. maybe input a list?
  f = lambda r: tmv.fv(400 / (1+r) + 500 / (1+r)**2 + 1000 / (1+r)**3, r, 3)
  calculates the future value of an annuity with specific deposit amounts.

The price today for a stock given risk rate, expected dividends, and expected future price. Also rearranged to solve for anything else.
  P_0 = (Div_1 + P_1) / (1 + r_E)
  Where P_0 is the current price,
    P_1 is the future sell price
    r_E is the risk rate.

The capital gain rate for a stock
  capital_gain_rate = (P_1-P_0)/P_0
  Where P_0 is the current price and P_1 is the future expected price.

The total return of a stock
  total_return = (Div_1/P_0) + capital_gain_rate(P_0, P_1)
  Where Div_1 is the expected dividend at the end of the year,
    P_0 is the current price,
    P_1 is the expected future sell price.

Dividend Yield formula for arbitrary number of years and arbitrary dividend payments each year.


"""


    
