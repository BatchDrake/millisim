from common import *

from millsim.HaloMergerDownloader import HaloMergerDownloader
from millsim.HaloMergerPlotter import HaloMergerPlotter

dl = HaloMergerDownloader()
dl.set_count(HALO_COUNT)
rang = (1e11, 1e12)
figno = 1

for rang in HALO_MASS_RANGES:
    try:
       print(\
             "Retrieving {0} haloes from {1:e} to {2:e} Msun... "\
             .format(HALO_COUNT, rang[0], rang[1]), end="", flush=True)
       
       dl.download_mass_range(rang)
       print("OK")
        
       haloes = dl.get_halo_history()
       
       if len(haloes) == 0:
           raise Exception("no haloes in this mass range")
       
       plotter = HaloMergerPlotter(haloes)
       plotter.plotHaloTree(figno, list(haloes.keys())[0])
       figno += 1
       
    except Exception as e:
       print("error: " + str(e))
       traceback.print_last()
        
plotter = HaloMergerPlotter(haloes)
plotter.plotVds(figno)
        
plt.show()
        
