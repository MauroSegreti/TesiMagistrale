"""
Fabbrica degli istogrammi: una griglia (bin eta) x (bin pT).
Ogni combinazione ha il proprio TH1F della risoluzione in curvatura.
"""

import ROOT
from config import PT_BINS, ETA_BINS


def build_histogram_grid():
    """
    Ritorna un dict:
        { indice_bin_eta: [istogramma_bin_pt_0, istogramma_bin_pt_1, ...] }
    """
    histos = {}
    for e_i, e in enumerate(ETA_BINS):
        histos[e_i] = []
        for p in PT_BINS:
            h = ROOT.TH1F(f"h_res_eta_{e_i}_{p['name']}", "", 100, -0.3, 0.3)
            histos[e_i].append(h)
    return histos
