from common import *

from millsim.GalaxyTreeDownloader import GalaxyTreeDownloader
from millsim.GalaxyPlotter import GalaxyPlotter

dl = GalaxyTreeDownloader()
dl.set_count(GALAXY_COUNT)
rang = (1e11, 1e12)
figno = 1

for rang in GALAXY_MASS_RANGES:
    try:
        print(\
              "Retrieving {0} galaxies from {1:e} to {2:e} Msun... "\
              .format(GALAXY_COUNT, rang[0], rang[1]), end="", flush=True)

        dl.download_mass_range(rang)
        print("OK")
        
        galaxies = dl.get_galaxy_history()
        
        if len(galaxies) == 0:
            raise Exception("no galaxies in this mass range")
        
        plotter = GalaxyPlotter(galaxies)
        plotter.plotGalaxyTree(figno, list(galaxies.keys())[0])
        figno += 1
        
    except Exception as e:
        print("error: " + str(e))
        traceback.print_last()

plt.show()