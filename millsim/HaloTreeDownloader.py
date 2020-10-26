# -*- coding: utf-8 -*-
from millsim import DataDownloader

class HaloTreeDownloader(DataDownloader.DataDownloader):
    def __init__(self, min_mass = 1e11, max_mass = 1e12):
        DataDownloader.DataDownloader.__init__(self)
        self.count = 10
        self.halos = {}
        self.have_halos = True
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
    
    def set_count(self, count):
        self.ensure_numeric(count, "halo count")
        self.count = count
        self.compose_query()

    
    def get_halo_history(self):
        if not self.have_halos:
            self.halos = {}
            for i in self.rows:
                finalHaloId = int(i[0])
                
                if (float(i[2]) < 1):
                    continue
                
                if not finalHaloId in self.halos:
                    self.halos[finalHaloId] = {}
                    
                for j in range(len(self.column_names)):
                    colname = self.column_names[j]
                    if not colname in self.halos[finalHaloId]:
                        self.halos[finalHaloId][colname] = []
                    
                    try:
                        self.halos[finalHaloId][colname].append(float(i[j]))
                    except:
                        self.halos[finalHaloId][colname].append(i[j])
            self.have_halos = True
            
        return self.halos
    
    def compose_query(self):
        self.have_halos = False
        self.query = """
        -- Crear tabla temporal que relaciona los halos con sus ramas principales                     
        select 
            DES.haloId,
            min(PROG.lastProgenitorId) as mainLeafId 
              into #mainBranches 
        from millimil..MPAHalo PROG, millimil..MPAHalo DES                         
        where                                                                                         
            DES.haloId in (
               select top {0} haloId from millimil..MPAHalo 
               where 
                   snapnum = 63 
                   and m_Crit200 between {1}/0.73e10 
                   and {2}/0.73e10 
                   and random between 0 and 100)                                                                    
            and PROG.haloId between DES.haloId and DES.lastProgenitorId 
        group by DES.haloId;                      
                     
        -- Hacer la búsqueda directamente en un JOIN                     
        select                         
            DES.haloId as finalHaloId,
            PROG.haloId,
            PROG.m_Crit200*0.73e10 as Msun,
            PROG.snapnum    
              into #haloEvolution   
        from millimil..MPAHalo PROG, millimil..MPAHalo DES         
        inner join #mainBranches as mb on (mb.haloId = DES.haloId)                                 
        where                                           
           PROG.haloId between DES.haloId and mb.mainLeafId;   
   
        -- Join de la evolución de los halos con la información del redshift
        select * from #haloEvolution 
        inner join 
            millimil..snapshots as snp 
            on (snp.snapnum = #haloEvolution.snapnum);
        """.format(self.count, self.min_mass, self.max_mass)
        self.set_query(self.query)
    
    def set_mass_range(self, min_mass, max_mass):
        self.ensure_numeric(min_mass, "minimum mass")
        self.ensure_numeric(max_mass, "maxumum mass")
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.compose_query()
