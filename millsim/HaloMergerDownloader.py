# -*- coding: utf-8 -*-
from millsim import DataDownloader
from millsim.constants import MILLSIM_h

class HaloMergerDownloader(DataDownloader.DataDownloader):
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
    
    def ensure_halo_history(self):
        if not self.have_haloes:
            self.haloes = {}
            for i in self.rows:
                finalId = int(i[0])
                
                if not finalId in self.haloes:
                    self.haloes[finalId] = {}
                    
                for j in range(len(self.column_names)):
                    colname = self.column_names[j]
                    if not colname in self.haloes[finalId]:
                        self.haloes[finalId][colname] = []
                    
                    try:
                        self.haloes[finalId][colname].append(float(i[j]))
                    except:
                        self.haloes[finalId][colname].append(i[j])
            self.have_haloes = True

    def get_halo_history(self):
        self.ensure_halo_history()
            
        return self.haloes

    def get_halo_ids(self):
        return list(self.get_halo_history().keys())
        
    def set_count(self, count):
        self.ensure_numeric(count, "halo count")
        self.count = count
        self.compose_query()
        
    def compose_query(self):
        self.have_haloes = False
        self.query = """
        -- Create halo tree tables                     
        select                                                                       
          DES.haloId as treeId,
          PROG.haloId,
          PROG.descendantId,
          PROG.m_Crit200*{3}e10 as Msun,
          PROG.snapnum,
          PROG.velDisp
          into #haloTrees 
        from                                                                                  
           millimil..MPAHalo PROG,                                                                      
           millimil..MPAHalo DES                         
        where                                                                                         
            DES.haloId in (
                select top {0} haloId 
                from millimil..MPAHalo
                where 
                    snapnum = 63 
                    and m_Crit200 between {1}/{3}e10 and {2}/{3}e10 
                    and random between 0 and 100)                                                                    
            and PROG.haloId between DES.haloId and DES.lastProgenitorId;                      

        -- Join halo tree to the snapshot info
        select * from #haloTrees 
        inner join 
            millimil..snapshots as snp 
            on (snp.snapnum = #haloTrees.snapnum);
        """.format(self.count, self.min_mass, self.max_mass, MILLSIM_h)
        self.set_query(self.query)


    def set_mass_range(self, min_mass, max_mass):
        self.ensure_numeric(min_mass, "minimum mass")
        self.ensure_numeric(max_mass, "maxumum mass")
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.compose_query()
