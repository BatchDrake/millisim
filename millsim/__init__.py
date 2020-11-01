# -*- coding: utf-8 -*-
"""
===
Millsim
===

Millennium Simulation abstraction project
"""

__version__ = "0.0.1"

import sys
if sys.version_info[0] < 3:
    sys.stderr.write("Preemptively aborting: you should not be uusing Python 2x in 2020")
    sys.exit()

from matplotlib import rcParams
defaultFont = 'Times New Roman'
rcParams['font.family'] = defaultFont
rcParams['mathtext.fontset'] = 'cm'
rcParams['text.usetex'] = True
rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}'] #for \text command

