# -*- coding: utf-8 -*-
from matplotlib import rcParams

defaultFont = 'Times New Roman'
rcParams['font.family'] = defaultFont
rcParams['mathtext.fontset'] = 'cm'
rcParams['text.usetex'] = True
rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}'] #for \text command

from matplotlib import pyplot as plt
import numpy as np 

TIMESTEPS = 64

class HaloPlotter:
    def __init__(self, halos):
        self.set_axes(plt.gca())
        self.processHalos(halos)

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
    
    def plotHalos(self, fig, title="Dark matter halo masses"):
        plt.figure(fig)
        self.ax.grid()
        
        for haloId in self.haloMass:
            z = self.haloZ[haloId] 
            m = self.haloMass[haloId]
        
            self.ax.set_title(title) 
            self.ax.set_xlabel('$\\text{log}_{10}(z + 1)$') 
            self.ax.set_ylabel('$\\text{log}_{10}[M_{main}(z)/M_0]$')

            M0 = m[TIMESTEPS - 1]
            self.ax.plot(np.log10(1 + z), np.log10(m / M0))

    def plotHaloMean(self, fig, title="Average dark matter halo mass", errorbar = False):
        plt.figure(fig)
        plt.grid(True)
        
        z = list(self.haloZ.values())[0]
        m = self.haloMassMean
        mErr = self.haloMassStd
        
        self.ax.set_title(title) 
        self.ax.set_xlabel('$\\text{log}_{10}(z + 1)$') 
        self.ax.set_ylabel('$\\text{log}_{10}[M_{main}(z)/M_0]$')

        M0 = m[TIMESTEPS - 1]
        
        x = np.log10(1 + z)
        y = np.log10(m / M0)
        
        self.ax.plot(x, y)
        
        if errorbar:
            yerr = np.log10((m + mErr) / m)
            self.ax.fill_between(x, y - yerr, y + yerr, alpha = 0.3)
        
        return
    
    def sanitizeNulls(self, dic, ignore = []):
        for key in dic:
            # Nulls are possible. In this case, we look for them and, if
            # any, we go ahead and perform a piecewise interpolation based on
            # the position of non null elements
            values = dic[key]
            
            nonNulls = values != 0
            if len(ignore) > 0:
                nonNulls[ignore] = True
            nulls    = ~nonNulls
            
            if len(nonNulls) == 0:
                raise Exception("Halo mass history is void. Cannot sanitize masses.")
            
            x_p = nonNulls.ravel().nonzero()[0] # Indices of valid masses
            y_p = values[x_p]                   # Values of valid masses
            z_p = nulls.ravel().nonzero()[0]    # Indices on null masses
            
            values[nulls] = np.interp(z_p, x_p, y_p)
            
    def processHalos(self, halos):
        self.haloMass = {}
        self.haloZ    = {}
        
        # Convert halos to a dictionary of vectors
        for haloId in halos:
            Z         = np.array(halos[haloId]["Z"])
            masses    = np.array(halos[haloId]["Msun"])
            snapNums  = np.array(halos[haloId]["snapnum"]).astype(int)
            
            self.haloMass[haloId] = np.zeros(TIMESTEPS)
            self.haloZ[haloId]  = np.zeros(TIMESTEPS)
            
            self.haloMass[haloId][snapNums] = np.array(masses)
            self.haloZ[haloId][snapNums]    = np.array(Z)
            
        # Remove nulls
        self.sanitizeNulls(self.haloMass)
        self.sanitizeNulls(self.haloZ, [TIMESTEPS - 1])
        
        # Compute halo mass mean and standard deviation
        haloMassMatrix = np.array(list(self.haloMass.values()))
        haloMassLast   = haloMassMatrix[:, [TIMESTEPS - 1]]
        haloMassMatrixNorm = (haloMassMatrix * haloMassLast ** -1)
        self.haloMassMean  = haloMassMatrixNorm.mean(0)
        self.haloMassStd   = haloMassMatrixNorm.std(0)
        