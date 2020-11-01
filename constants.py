# Constants shared by all exercices

HALO_COUNT  = 25 # Number of halos to download for each mass range
HALO_MASS_RANGES = [   \
    (0, 1e10),    \
    (1e10, 1e11), \
    (1e11, 1e12), \
    (1e12, 1e13), \
    (1e13, 1e30)]

GALAXY_COUNT = HALO_COUNT
GALAXY_MASS_RANGES = HALO_MASS_RANGES