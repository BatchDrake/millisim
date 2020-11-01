# Constants shared by all exercices

HALO_COUNT  = 25 # Number of halos to download for each mass range
HALO_MASS_RANGES = [   \
    (0, 1e10),    \
    (1e10, 1e11), \
    (1e11, 1e12), \
    (1e12, 1e13), \
    (1e13, 1e30)]

GALAXY_COUNT = HALO_COUNT

GALAXY_TO_HALO_MASS_RATIO = 1e-2 # Trust me, I'm an engineer
GALAXY_MASS_RANGES = []

for r in HALO_MASS_RANGES:
    GALAXY_MASS_RANGES.append(\
        (GALAXY_TO_HALO_MASS_RATIO * r[0], GALAXY_TO_HALO_MASS_RATIO * r[1]))

GALAXY_MASS_RANGES.append((1e11, 1e12))
GALAXY_MASS_RANGES.append((2e11, 1e30))
