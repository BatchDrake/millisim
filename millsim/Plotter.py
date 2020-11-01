# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import numpy as np 

class Plotter:
    def __init__(self):
        self.set_axes(plt.gca())

    def set_axes(self, axes):
        self.ax = axes
            
    def quantityToLatex(self, q):
        sign = ""
        if q < 0:
            q = -q
            sign = "-"
            
        if q < 10:
            return sign + str(q)
        
        exp = int(np.floor(np.log10(q)))
        mul = 10 ** -exp
        return "$" + sign + "{0:g}\\times 10^{{{1:d}}}$".format(q * mul, exp)
    
    def sanitizeNulls(self, dic, ignore = []):
        illEntries = []
        for key in dic:
            # Nulls are possible. In this case, we look for them and, if
            # any, we go ahead and perform a piecewise interpolation based on
            # the position of non null elements
            values = dic[key]
            
            nonNulls = values != 0
            if len(ignore) > 0:
                nonNulls[ignore] = True
            nulls    = ~nonNulls
            
            x_p = nonNulls.ravel().nonzero()[0] # Indices of valid masses
            y_p = values[x_p]                   # Values of valid masses
            z_p = nulls.ravel().nonzero()[0]    # Indices on null masses
            
            # Check if this entry can be sanitized. If not, append to the
            # illEntries list and remove it
            if len(x_p) == 0:
                illEntries.append(key)
            else:
                values[nulls] = np.interp(z_p, x_p, y_p)
                
        for i in illEntries:
            del dic[i]