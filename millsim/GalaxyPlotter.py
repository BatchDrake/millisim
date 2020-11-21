# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
import numpy as np 
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from millsim import Plotter
from millsim.constants import MILLSIM_OVERCOLOR
from millsim.colors import bv2rgb, rgb2html

class GalaxyPlotter(Plotter.Plotter):
    def __init__(self, galaxies):
        Plotter.Plotter.__init__(self)
        self.processGalaxies(galaxies)
    
    def nodeName(self, gId):
        return "galaxy_{0}".format(int(gId))

    def galaxyIsValid(self, gId, ndx):
        ret = self.galaxyMass[gId][ndx] > 1
        return ret
    
    def plotGalaxyTree(self, fig, gId):
        plt.figure(fig)
        G = nx.DiGraph()
        
        node_color = []
        node_size  = []
        edge_color = []
        
        # Add nodes
        for ndx, i in enumerate(self.galaxyEdges[gId]):
            if self.galaxyIsValid(gId, ndx):
                child  = self.nodeName(i[0])
                color = rgb2html(bv2rgb(MILLSIM_OVERCOLOR * self.galaxyBV[gId][ndx]))
                logsz = (np.log10(1 + self.galaxyMass[gId][ndx]) - 5)
                
                if logsz < 2:
                    logsz = 2
                    
                node_size.append(10 * logsz * logsz)
                node_color.append(color)
                G.add_node(child, back_color=color)

        # Add edges (in black, of course)
        for ndx, i in enumerate(self.galaxyEdges[gId]):
            if self.galaxyIsValid(gId, ndx) and int(i[1]) >= 0:
                child  = self.nodeName(i[0])
                parent = self.nodeName(i[1])
                edge_color.append('k')
                G.add_edge(child, parent)

        # Oh my God, networkx is so broken
        pos = graphviz_layout(G, prog = 'dot')
        for ndx, i in enumerate(self.galaxyEdges[gId]):
            if self.galaxyIsValid(gId, ndx):
                child  = self.nodeName(i[0])
                pos[child] = (pos[child][0], self.galaxyLBTime[gId][ndx])

        nx.draw_networkx(               \
            G,                          \
            pos,                        \
            edge_color = edge_color,    \
            node_color = node_color,    \
            node_size = node_size,      \
            with_labels = False,        \
            arrows = False)
        
        # Add axes and stuff
        ax = plt.gca()
        ax.collections[0].set_edgecolor("#000000")
        ax.set_ylabel('Lookback time (Gyr)')
        ax.tick_params(left = True, labelleft = True)
        title = 'Galaxy merger history (resulting stellar mass: ' + \
        self.quantityToLatex(self.galaxyMass[gId][0]) + \
        ' $M_\odot$)' 
        
        plt.title(title)
        plt.axis(True)
        plt.grid(True)
        plt.ylim(-1, 14)
        
    def processGalaxies(self, galaxies):
        self.galaxyMass    = {}
        self.galaxyBV      = {}
        self.galaxyEdges   = {}
        self.galaxySnapNrs = {}
        self.galaxyLBTime  = {}
        # Convert galaxies to a dictionary of vectors
        for galaxyId in galaxies:
            masses    = np.array(galaxies[galaxyId]["stellarMsun"])
            bv        = np.array(galaxies[galaxyId]["B_V"])
            lbTime    = np.array(galaxies[galaxyId]["lookbackTime"])
            snapNums  = np.array(galaxies[galaxyId]["snapnum"]).astype(int)
            
            edges = []
            for ndx, gId in enumerate(galaxies[galaxyId]["galaxyId"]):
                edges.append((gId, galaxies[galaxyId]["descendantId"][ndx]))
                
            self.galaxyEdges[galaxyId]   = edges
            self.galaxyMass[galaxyId]    = masses
            self.galaxyBV[galaxyId]      = bv
            self.galaxySnapNrs[galaxyId] = snapNums
            self.galaxyLBTime[galaxyId]  = lbTime
        
    
