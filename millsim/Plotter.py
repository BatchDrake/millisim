# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import numpy as np
from scipy.interpolate import interp1d 
from millsim.constants import MILLSIM_TIMESTEPS

def zero_order_hold(x, xp, yp):
    xmin = np.min(xp)
    f = interp1d(xp, yp, kind='zero', fill_value='extrapolate', assume_sorted=False)
    return np.where(x < xmin, np.nan, f(x))

class Plotter:
    def __init__(self):
        self.set_axes(plt.gca())
        self.zDict = {}
        self.zDict[MILLSIM_TIMESTEPS - 1] = 0.
        self.zTable = np.array(0)
        self.zAxis  = np.array(0)
        
    def set_axes(self, axes):
        self.ax = axes
            
    def quantityToLatex(self, q):
        sign = ""
        if q < 0:
            q = -q
            sign = "-"
            
        if q < 10:
            return "$" + sign + "{0:g}$".format(q)
        elif q > 1e25:
            return "$" + sign + "\\infty$"
        
        exp = int(np.floor(np.log10(q)))
        mul = 10 ** -exp
        return "$" + sign + "{0:g}\\times 10^{{{1:d}}}$".format(q * mul, exp)
        
    def updateZ(self, snapNums, z):
        if self.zTable.size == 0:
            i = 0
            while len(self.zDict) < MILLSIM_TIMESTEPS and i < len(z):
                sn = int(snapNums[i])
                if not self.zDict.has_key(sn):
                    self.zDict[sn] = z[i]
                i += 1
            
            
            if len(self.zDict) == MILLSIM_TIMESTEPS:
                i = 0
                self.zTable = np.array(MILLSIM_TIMESTEPS)
                while i < MILLSIM_TIMESTEPS:
                    self.zTable[i] = self.zDict[i]
                
                self.zAxis = np.flip(self.zTable)
                
    def translateZ(self, snapnums):
        if len(self.zDict) == MILLSIM_TIMESTEPS:
            return self.zTable[snapnums]
        else:
            return np.interp(\
                    snapnums, \
                    np.array(self.zDict.keys()), \
                    np.array(self.zDict.values()))

    def getZAxis(self):
        if len(self.zDict) == MILLSIM_TIMESTEPS:
            return self.zAxis
        else:
            return self.translateZ(np.flip(np.arange(0, MILLSIM_TIMESTEPS)))
        
    def sanitizeNulls(self, dic, ignore = [], hold = False):
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
            elif hold:
                values[nulls] = zero_order_hold(z_p, x_p, y_p)
            else:
                values[nulls] = np.interp(z_p, x_p, y_p)
                
        for i in illEntries:
            del dic[i]