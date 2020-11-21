# -*- coding: utf-8 -*-
from millsim import DataDownloader
from millsim.constants import MILLSIM_TIMESTEPS
import numpy as np 

class TimeAxisDownloader(DataDownloader.DataDownloader):
    def __init__(self):
        DataDownloader.DataDownloader.__init__(self)
        self.set_query("SELECT snapNum,Z FROM millimil..snapshots")
        self.haveAxis = False
        
    def ensureAxis(self):
        if not self.haveAxis:
            self.download()
            if self.row_count() != MILLSIM_TIMESTEPS:
                raise Exception("Unexpected number of time steps")
            
            self.timeAxis = np.array(self.column("Z"))
            self.haveAxis = True
            
    def getTimeAxis(self):
        self.ensureAxis()
        return self.timeAxis
    