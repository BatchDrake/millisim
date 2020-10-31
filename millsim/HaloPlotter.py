# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np 

class HaloPlotter:
    def __init__(self, halos):
        self.halos = halos
        self.processHalos()

    def plotHalos(self, fig, title="Dark matter halo masses"):
        plt.figure(fig)
        plt.grid(True)
        for haloId in self.halos:
            masses = self.halos[haloId]["Msun"]
            redshifts = self.halos[haloId]["Z"]
            z = np.array(redshifts) 
            m = np.array(masses)
        
            plt.title(title) 
            plt.xlabel("log(z + 1)") 
            plt.ylabel("log[Mmain(z)/M0]")
            plt.axis("auto") 
            M0 = m[0]
            plt.plot(np.log(1 + z), np.log(m / M0))

    def plotHaloMean(self, fig, title="Average dark matter halo mass"):
        return
    
    def sanitizeMasses(self):
        for haloId in self.halos:
            prev = 0
            masses = self.halos[haloId]["Msun"]
            massCount = len(masses)
            
            for i in range(massCount):
                curr = masses[i]   
                if curr < 1:
                    masses[i] = curr = prev
                prev = curr
                
    def processHalos(self):
        self.sanitizeMasses()
        return