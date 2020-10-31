from matplotlib import pyplot as plt 
from millsim import HaloTreeDownloader, HaloPlotter
import traceback
import sys

HALO_COUNT  = 25
MASS_RANGES = [\
    (0, 1e10), (1e10, 1e11), (1e11, 1e12), (1e12, 1e13), (1e13, 1e30)]

dl     = HaloTreeDownloader.HaloTreeDownloader()
figno  = 1
legend = []

dl.set_count(HALO_COUNT)

for i in MASS_RANGES:
    print(\
          "Retrieving {0} halos from {1:e} to {2:e} Msun... "\
          .format(HALO_COUNT, i[0], i[1]), end="", flush=True)
    
    try:
        dl.download_mass_range(i)
        halos = dl.get_halo_history()
        print("OK: {0} rows, {1} halos".format(dl.row_count(), len(halos)))

        plotter = HaloPlotter.HaloPlotter(halos)
        
        legend.append(\
            "{0} $M_\odot$ to {1} $M_\odot$".format( \
            plotter.quantityToLatex(i[0]), plotter.quantityToLatex(i[1])))
                
        plotter.plotHaloMean(figno, "Halo mass evolution (mean)", False)

    except Exception as e:
        print("error: " + str(e))
        
plt.legend(legend)
plt.show()
    