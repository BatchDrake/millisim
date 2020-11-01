# -*- coding: utf-8 -*-
from millsim import DataDownloader
from millsim.constants import MILLSIM_h

class GalaxyTreeDownloader(DataDownloader.DataDownloader):
    def __init__(self, min_mass = 1e11, max_mass = 1e12):
        DataDownloader.DataDownloader.__init__(self)
        self.count = 10
        self.set_mass_range(min_mass, max_mass)

    def download_mass_range(self, *rang):
        if len(rang) == 1:
            if not isinstance(rang, tuple) and not isinstance(rang, list):
                raise Exception("Invalid range type. Must be tuple or list")
            min_mass = rang[0][0]
            max_mass = rang[0][1]
        elif len(rang) == 2:
            min_mass = rang[0]
            max_mass = rang[1]
        else:
            raise Exception("Invalid number of arguments")
        
        self.set_mass_range(min_mass, max_mass)
        return self.download()
    
    def ensure_galaxy_history(self):
        if not self.have_galaxies:
            self.galaxies = {}
            for i in self.rows:
                finalId = int(i[0])
                
                if not finalId in self.galaxies:
                    self.galaxies[finalId] = {}
                    
                for j in range(len(self.column_names)):
                    colname = self.column_names[j]
                    if not colname in self.galaxies[finalId]:
                        self.galaxies[finalId][colname] = []
                    
                    try:
                        self.galaxies[finalId][colname].append(float(i[j]))
                    except:
                        self.galaxies[finalId][colname].append(i[j])
            self.have_galaxies = True

    def get_galaxy_history(self):
        self.ensure_galaxy_history()
            
        return self.galaxies

    def get_galaxy_ids(self):
        return list(self.get_galaxy_history().keys())
        
    def set_count(self, count):
        self.ensure_numeric(count, "galaxy count")
        self.count = count
        self.compose_query()
        
    def compose_query(self):
        self.have_galaxies = False
        self.query = """
        -- Create galaxy tree tables                     
        select                                                                       
          DES.galaxyId as treeId,
          PROG.galaxyId,
          PROG.descendantId,
          PROG.stellarMass*{3}e10 as stellarMsun,
          PROG.snapnum,
          PROG.mag_b - PROG.mag_v as B_V   
          into #galaxyTrees 
        from                                                                                  
           millimil..DeLucia2006a PROG,                                                                      
           millimil..DeLucia2006a DES                         
        where                                                                                         
            DES.galaxyId in (
                select top {0} galaxyId 
                from millimil..DeLucia2006a 
                where 
                    snapnum = 63 
                    and stellarMass between {1}/{3}e10 and {2}/{3}e10 
                    and random between 0 and 100)                                                                    
            and PROG.galaxyId between DES.galaxyId and DES.lastProgenitorId;                      

        -- Join galaxy tree to the snapshop info
        select * from #galaxyTrees 
        inner join 
            millimil..snapshots as snp 
            on (snp.snapnum = #galaxyTrees.snapnum);
        """.format(self.count, self.min_mass, self.max_mass, MILLSIM_h)
        self.set_query(self.query)


    def set_mass_range(self, min_mass, max_mass):
        self.ensure_numeric(min_mass, "minimum mass")
        self.ensure_numeric(max_mass, "maxumum mass")
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.compose_query()
