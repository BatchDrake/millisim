# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import numpy as np 
from millsim import Plotter
from millsim.constants import *

class HaloPlotter(Plotter.Plotter):
    def __init__(self, halos, massColumn = "Msun"):
        Plotter.Plotter.__init__(self)
        self.massColumn = massColumn
        self.processHalos(halos)
    
    def plotHalos(self, fig, title="Dark matter halo masses"):
        plt.figure(fig)
        self.ax.grid()
        
        for haloId in self.haloMass:
            z = self.haloZ[haloId] 
            m = self.haloMass[haloId]
        
            self.ax.set_title(title) 
            self.ax.set_xlabel('$\\text{log}_{10}(z + 1)$') 
            self.ax.set_ylabel('$\\text{log}_{10}[M_{main}(z)/M_0]$')

            M0 = m[MILLSIM_TIMESTEPS - 1]
            self.ax.plot(np.log10(1 + z), np.log10(m / M0))

    def plotHaloMean(self, fig, title="Halo mass in $M_\\odot$", errorbar = False):
        plt.figure(fig)
        plt.grid(True)
        
        z = list(self.haloZ.values())[0]
        m = self.haloMassMean
        mErr = self.haloMassStd
        
        self.ax.set_title(title) 
        self.ax.set_xlabel('$\\text{log}_{10}(z + 1)$') 
        self.ax.set_ylabel('$\\text{log}_{10}[M_{main}(z)/M_0]$')

        M0 = m[MILLSIM_TIMESTEPS - 1]
        
        x = np.log10(1 + z)
        y = np.log10(m / M0)
        
        self.ax.plot(x, y)
        
        if errorbar:
            yerr = np.log10((m + mErr) / m)
            self.ax.fill_between(x, y - yerr, y + yerr, alpha = 0.3)
        
    def processHalos(self, halos):
        self.haloMass = {}
        self.haloZ    = {}
        
        # Convert halos to a dictionary of vectors
        for haloId in halos:
            Z         = np.array(halos[haloId]["Z"])
            masses    = np.array(halos[haloId][self.massColumn])
            snapNums  = np.array(halos[haloId]["snpnr"]).astype(int)
            
            self.haloMass[haloId] = np.zeros(MILLSIM_TIMESTEPS)
            self.haloZ[haloId]  = np.zeros(MILLSIM_TIMESTEPS)
            
            self.haloMass[haloId][snapNums] = np.array(masses)
            self.haloZ[haloId][snapNums]    = np.array(Z)
            
        # Remove nulls
        self.sanitizeNulls(self.haloMass)
        self.sanitizeNulls(self.haloZ, [MILLSIM_TIMESTEPS - 1])
        
        # Compute halo mass mean and standard deviation
        haloMassMatrix = np.array(list(self.haloMass.values()))
        haloMassLast   = haloMassMatrix[:, [MILLSIM_TIMESTEPS - 1]]
        haloMassMatrixNorm = (haloMassMatrix * haloMassLast ** -1)
        self.haloMassMean  = haloMassMatrixNorm.mean(0)
        self.haloMassStd   = haloMassMatrixNorm.std(0)
        