# -*- coding: utf-8 -*-
from millsim import DataDownloader

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
    
        
    def set_count(self, count):
        self.ensure_numeric(count, "galaxy count")
        self.count = count
        self.compose_query()
        
    def compose_query(self):
        self.query = """
        -- Crear tabla temporal que relaciona las galaxias con sus ramas principales                     
        select                                                                       
          DES.galaxyId,
          min(PROG.lastProgenitorId) as mainLeafId 
          into #mainBranches 
        from                                                                                  
           millimil..DeLucia2006a PROG,                                                                      
           millimil..DeLucia2006a DES                         
        where                                                                                         
            DES.galaxyId in (
                select top {0} galaxyId 
                from millimil..DeLucia2006a 
                where 
                    snapnum = 63 
                    and stellarMass between {1}/0.73e10 
                    and {2}/0.73e10 
                    and random between 0 and 100)                                                                    
            and PROG.galaxyId between DES.galaxyId 
            and DES.lastProgenitorId 
        group by DES.galaxyId;                      
                     
        -- Hacer la búsqueda directamente en un JOIN                     
        select                         
            DES.galaxyId as finalGalaxyId,
            PROG.galaxyId,
            PROG.stellarMass*0.73e10 as Msun,PROG.snapnum    
        into #galaxyEvolution   
        from                                    
            millimil..DeLucia2006a PROG,                        
            millimil..DeLucia2006a DES         
        inner join #mainBranches as mb on (mb.galaxyId = DES.galaxyId)                                 
        where                                           
            PROG.galaxyId between DES.galaxyId 
            and mb.mainLeafId;   
   
        -- Join galaxy evolution data with snapshot information   
        select * from #galaxyEvolution 
        inner join 
            millimil..snapshots as snp 
            on (snp.snapnum = #galaxyEvolution.snapnum);
        """.format(self.count, self.min_mass, self.max_mass)
        self.set_query(self.query)


    def set_mass_range(self, min_mass, max_mass):
        self.ensure_numeric(min_mass, "minimum mass")
        self.ensure_numeric(max_mass, "maxumum mass")
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.compose_query()
