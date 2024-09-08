# -*- coding: utf-8 -*-
"""
Option pricing & greeks using Mibian

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

#!pip install mibian

import mibian

up = 42661.2
strike = 42700
ir = 0.07
time_to_expiry = 17.986 #this needs to be in days and not years
option_price = 435.7
option_type = "CE"

mbo = mibian.BS([up, strike, ir, time_to_expiry], callPrice= option_price)
imp_vol = mbo.impliedVolatility

mbo = mibian.BS([up, strike, 0.07, time_to_expiry], volatility= mbo.impliedVolatility)
delta = mbo.callDelta if option_type =="CE" else mbo.putDelta
theta =mbo.callTheta if option_type=="CE" else mbo.putTheta
vega =mbo.vega
gamma =mbo.gamma