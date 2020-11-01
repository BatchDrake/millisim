# -*- coding: utf-8 -*-
from millsim import DataDownloader
from millsim.constants import MILLSIM_h

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
                   and m_Crit200 between {1}/{3}e10 and {2}/{3}e10 
                   and random between 0 and 100)                                                                    
            and PROG.haloId between DES.haloId and DES.lastProgenitorId 
        group by DES.haloId;                      
                     
        -- Hacer la búsqueda directamente en un JOIN                     
        select                         
            DES.haloId as finalHaloId,
            PROG.haloId as intHaloId,
            PROG.m_Crit200*{3}e10 as Msun,
            PROG.snapnum as snpnr  
        into #haloEvolution   
        from millimil..MPAHalo PROG, millimil..MPAHalo DES         
        inner join #mainBranches as mb on (mb.haloId = DES.haloId)
        where                                           
           PROG.haloId between DES.haloId and mb.mainLeafId;   
        
        -- Extract galaxies in each halo along with their stelar masses
        select
            intHaloId,
            galaxyID,
            stellarMass,
            coldGas,
            hotGas
        into #galaxyMasses
        from #haloEvolution
        left outer join millimil..DeLucia2006a as galaxies on (galaxies.haloID = intHaloId);
        
        -- Compute halo stellar masses by summing the masses of each individual galaxy
        select
            intHaloId,
            sum(stellarMass)*{3}e10 as stellarMsun,
            sum(coldGas + hotGas)*{3}e10 as gasMsun
        into #haloStarMasses
        from #galaxyMasses
        group by intHaloId;
        
        -- Append this information to haloEvolution and call it starMassEvolution
        select
            #haloEvolution.*,
            stellarMsun,
            gasMsun,
            stellarMsun + gasMsun as baryonMsun,
            (stellarMsun + gasMsun) / (Msun + 1) as baryonMassFraction
        into #starMassEvolution
        from #haloEvolution
        inner join #haloStarMasses on (#haloStarMasses.intHaloId = #haloEvolution.intHaloId);
        
        -- Join de la evolución de los halos con la información del redshift
        select * from #starMassEvolution 
        inner join 
            millimil..snapshots as snp 
    on (snp.snapnum = #starMassEvolution.snpnr);
        """.format(self.count, self.min_mass, self.max_mass, MILLSIM_h)
        self.set_query(self.query)
    
    def set_mass_range(self, min_mass, max_mass):
        self.ensure_numeric(min_mass, "minimum mass")
        self.ensure_numeric(max_mass, "maxumum mass")
        self.min_mass = min_mass
        self.max_mass = max_mass
        self.compose_query()
