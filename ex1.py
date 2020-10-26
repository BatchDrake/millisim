import numpy as np 
from matplotlib import pyplot as plt 
from millsim import HaloTreeDownloader

HALO_COUNT  = 10
MASS_RANGES = [\
    (0, 1e10), (1e10, 1e11), (1e11, 1e12), (1e12, 1e13), (1e13, 1e30)]

dl = HaloTreeDownloader.HaloTreeDownloader()

for i in MASS_RANGES:
    print(\
          "Retrieving {0} halos from {1:e} to {2:e} Msun... "\
          .format(HALO_COUNT, i[0], i[1]), end="", flush=True)
    
    try:
        dl.download_mass_range(i)
        halos = dl.get_halo_history()
        print("OK: {0} rows, {1} halos".format(dl.row_count(), len(halos)))
        
        for haloId in halos:
            masses = halos[haloId]["Msun"]
            redshifts = halos[haloId]["Z"]
            z = np.array(redshifts) 
            m = np.array(masses)
            
            plt.title("Halo evolution ({0:g} to {1:g} Msun)".format(i[0], i[1])) 
            plt.xlabel("log(z + 1)") 
            plt.ylabel("log[Mmain(z)/M0]")
            plt.axis("auto") 
            plt.plot(np.log(1 + z), np.log(m / np.max(m)))
        plt.show()
        
    except Exception as e:
        print("error: " + str(e))
