from common import *

from millsim.HaloTreeDownloader import HaloTreeDownloader
from millsim.HaloPlotter import HaloPlotter

dl     = HaloTreeDownloader()
legend = []

dl.set_count(HALO_COUNT)

for i in HALO_MASS_RANGES:
    print(\
          "Retrieving {0} halos from {1:e} to {2:e} Msun... "\
          .format(HALO_COUNT, i[0], i[1]), end="", flush=True)
    
    try:
        dl.download_mass_range(i)
        halos = dl.get_halo_history()
        print("OK: {0} rows, {1} halos".format(dl.row_count(), len(halos)))

        plotter = HaloPlotter(halos)
        
        legend.append(\
            "{0} $M_\odot$ to {1} $M_\odot$".format( \
            plotter.quantityToLatex(i[0]), plotter.quantityToLatex(i[1])))
                
        plotter.plotHaloMean(1, "Halo mass evolution (mean)", False)

    except Exception as e:
        print("error: " + str(e))
        
plt.legend(legend)
plt.show()
