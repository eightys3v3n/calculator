import unittest
import logging

import math
# sqrt()
# pow()

import locale
# for number formatting

import sympy
# for equation rearranging

import statistics
# stdev(arr) for std deviation

from . import finance
# a number of functions for my FNCE courses


locale.setlocale(locale.LC_ALL, '')
RESULT_PRECISION = 4 # How many decimals should we round results from formulas to
logging.basicConfig(level=logging.INFO)

global FUNCTIONS
FUNCTIONS = {} # contains all the cached function rearrangements


# General
def num_format(num):
    """Format a number using commas."""
    return "{:n}".format(num)


def all_functions(var, expr, vars):
    root_var = var
    root_expr = expr
    var = None
    expr = None
    functions = {}

    vars.sort(key=lambda v:v.name) # so we can predict the argument order
    root_eq = sympy.Eq(root_var, root_expr) # so we can rearrange it
    #print("Given equation:")
    #sympy.pprint(root_eq)
                  
    for var in vars:
        try:
            expr, = sympy.solve(root_eq, var)
        except NotImplementedError as e:
            print("No method found to solve for {} in equation".format(var))
            sympy.pprint(root_eq)
            continue
        if not expr:
            #print("Couldn't solve for {}".format(var.name))
            continue
        eq = sympy.Eq(var, expr)
        #print("Derived equation:")
        #sympy.pprint(eq)

        new_vars = vars.copy()
        new_vars.remove(var)
        functions[var.name] = sympy.lambdify(new_vars, expr)
    return functions    
        

"""
Things still required

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


    
