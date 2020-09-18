import math
import locale
locale.setlocale(locale.LC_ALL, '')


RESULT_PRECISION = 4 # How many decimals should we round results from formulas to


# General
def num_format(num):
    """Format a number using commas."""
    return "{:n}".format(num)


# Time Value of Money
class tmv:
    """Comparing present money with future money using interest rates."""
    
    def pv(*, fv, r, n):
        """The present value of a future amount of money. To discount the future money.
        fv: future value
        r: yearly interest rate during the whole period
        n: number of years in the future

        If we are going to be given $1000 in 8 years (a 2% interest rate the whole time):
          pv(1000, 0.02, 8) == $853.4904
          The money would currently be worth $853.49 if the interest rate stays at 2% over those 8 years.
        """
        _pv_ = fv / ((1+r)**n)
        _pv_ = round(_pv_, RESULT_PRECISION)
        return _pv_

    def fv(*, pv, r, n):
        """The future value of a present amount of money. To compound present money.
        pv: present value
        r: yearly interest rate over the whole period
        n: get the value in how many years

        If we are going to do a one time investment of $1000 for 8 years (2% interest the whole time):
          (1000, 0.02, 8) == $1171.6594
          We would have $1171.66 at the end of the eighth year.
        """
        _fv_ = pv * ((1+r)**n)
        _fv_ = round(_fv_, RESULT_PRECISION)
        return _fv_

class invest:
    """Calculations for investments."""

    class perpetuity:
        def pv_of(*, init, r):
            """The present  value of a perpetuity.
            init: the initial investment
            r: rate of return / discount rate
            
            If we invest $1,000 into a bank account at a guarenteed 2% interest rate:
              (init=1000, r=0.02) == 
              So the present value of such a perpetuity is $.
            """
            pv = init / r
            pv = round(pv, RESULT_PRECISION)
            return pv
    
    class annuity:
        """Calculations for annuities."""
        
        def pv_of(*, c, r, n):
            """The present value of an annuity (yearly deposits) using interest.
            c: the yearly deposit amount
               this is in money at the time of the deposit. so the first deposit
               is in money valued at the end of this year. the second deposit
               is in money valued at the end of next year.
            r: yearly interest rate
            n: number of years
            
            If we invest $1000 a year (at the end of the year) for 8 years (2% interest the whole time):
              (c=1000, r=0.02, n=8) == 7325.4814
              We would have $8582.97 in eight years and it would be worth $7325.48 in today dollars.
            """
            pv = c * 1/r * (1 - 1/(1+r)**n)
            pv = round(pv, RESULT_PRECISION)
            return pv

    
        def fv_of(*, c, r, n):
            """The future value of an annuity (yearly deposits) using interest.
            c: the yearly deposit amount.
               this is in money at the time of the deposit. so the first deposit
               is in money valued at the end of this year. the second deposit
               is in money valued at the end of next year.
            r: yearly interest rate
            n: number of years

            If we invest $1000 aa year (at the end of the year) for 8 years (2% interest the whole time):
              (1000, 0.02, 8) == 8582.9691
              We would have $8582.97 dollars in eight years which would be worth $7325.48 in today dollars.
            """
            fv = c * 1/r * ((1+r)**n - 1)
            fv = round(fv, RESULT_PRECISION)
            return fv

    
        def cashflow_of(*, fv, r, n):
            """The required monthly payment of an annuity to end up with fv dollars.
            fv: the amount of money you want to have in n years
            r: yearly interest rate
            n: in how many years do you want to have this money

            If we want to have $1,000 in 10 years at an interest rate of 2% the whole time:
              (fv=1,000, r=0.02, n=10) == 91.3265
              So we would have to save $91.33 every month to end up with $1,000 at the end of 10 years.
            """
            c = fv / (1/r * ((1+r)**n -1))
            c = round(c, RESULT_PRECISION)
            return c

    # need a function for n years with odd deposit amounts
    #f = lambda r: tmv.fv(400 / (1+r) + 500 / (1+r)**2 + 1000 / (1+r)**3, r, 3)
    # calculates the future value of an annuity with specific deposit amounts.

    # need a function to calculate the payment if we have the pv_of_annuity
        

class loan: pass
    
