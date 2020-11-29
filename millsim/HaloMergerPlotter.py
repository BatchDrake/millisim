# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np 
import networkx as nx
import math
from networkx.drawing.nx_agraph import graphviz_layout

from millsim import Plotter
from millsim.constants import MILLSIM_OVERCOLOR
from millsim.colors import bv2rgb, rgb2html

vdcm = plt.get_cmap('plasma')

def vd2rgb(vd):
    ndx = math.floor(vd / (300.) * vdcm.N)
    if ndx < 0:
        ndx = 0
    elif ndx >= vdcm.N:
        ndx = vdcm.N - 1
        
    return vdcm(ndx)[:3]

class HaloMergerPlotter(Plotter.Plotter):
    def __init__(self, haloes):
        Plotter.Plotter.__init__(self)
        self.processHaloes(haloes)
    
    def nodeName(self, gId):
        return "halo_{0}".format(int(gId))

    def haloIsValid(self, gId, ndx):
        return True
        ret = self.haloMass[gId][ndx] > 1
        return ret

    def plotVds(self, fig):
        plt.figure(fig)
        fig, ax = plt.subplots()

        ax = fig.add_subplot(111)
        for i in np.arange(0, 350, 50):
            y = i * .05
            x = 0

            circle = plt.Circle((x, y), radius = 1, facecolor = rgb2html(vd2rgb(i)), edgecolor = 'black')
            ax.add_patch(circle)

            label = ax.annotate("{0:g}".format(i), xy = (x, y), fontsize = 8, ha = "center", va = "center")

            ax.axis('off')
            ax.set_aspect('equal')
            ax.autoscale_view()

    def plotHaloTree(self, fig, gId):
        plt.figure(fig)
        G = nx.DiGraph()
        
        node_color = []
        node_size  = []
        edge_color = []
        
        # Add nodes
        for ndx, i in enumerate(self.haloEdges[gId]):
            if self.haloIsValid(gId, ndx):
                child = self.nodeName(i[0])
                color = rgb2html(vd2rgb(self.haloVD[gId][ndx]))
                logsz = (np.log10(self.haloMass[gId][ndx]) - 7)
                
                if logsz < 0:
                    logsz = 0
                    
                node_size.append(10 * logsz * logsz)
                node_color.append(color)
                G.add_node(child, back_color=color)

        # Add edges (in black, of course)
        for ndx, i in enumerate(self.haloEdges[gId]):
            if self.haloIsValid(gId, ndx) and int(i[1]) >= 0:
                child  = self.nodeName(i[0])
                parent = self.nodeName(i[1])
                edge_color.append('k')
                G.add_edge(child, parent)
        # Oh my God, networkx is so broken
        pos = graphviz_layout(G, prog = 'dot')
        for ndx, i in enumerate(self.haloEdges[gId]):
            if self.haloIsValid(gId, ndx):
                child  = self.nodeName(i[0])
                pos[child] = (pos[child][0], self.haloLBTime[gId][ndx])

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
        title = 'Halo merger history (resulting DM mass: ' + \
        self.quantityToLatex(self.haloMass[gId][0]) + \
        ' $M_\odot$)' 
        
        plt.title(title)
        plt.axis(True)
        plt.grid(True)
        plt.ylim(-1, 14)
        
    def processHaloes(self, haloes):
        self.haloMass    = {}
        self.haloVD      = {}
        self.haloEdges   = {}
        self.haloSnapNrs = {}
        self.haloLBTime  = {}
        # Convert haloes to a dictionary of vectors
        for haloId in haloes:
            masses    = np.array(haloes[haloId]["Msun"])
            vd        = np.array(haloes[haloId]["velDisp"])
            lbTime    = np.array(haloes[haloId]["lookbackTime"])
            snapNums  = np.array(haloes[haloId]["snapnum"]).astype(int)

            edges = []
            for ndx, gId in enumerate(haloes[haloId]["haloId"]):
                edges.append((gId, haloes[haloId]["descendantId"][ndx]))
                
            self.haloEdges[haloId]   = edges
            self.haloMass[haloId]    = masses
            self.haloVD[haloId]      = vd
            self.haloSnapNrs[haloId] = snapNums
            self.haloLBTime[haloId]  = lbTime
        
    
