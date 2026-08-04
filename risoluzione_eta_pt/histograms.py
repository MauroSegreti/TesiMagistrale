"""
Fabbrica della griglia di istogrammi N x M richiesta da Marco:
N = numero di bin in pT, M = numero di bin in eta.
Un istogramma per ogni combinazione (bin pT, bin eta).
"""

import ROOT
from config import PT_BINS, ETA_BINS


def build_histogram_grid():
    """
    Ritorna un dict:
        { nome_bin_pt: [istogramma_bin_eta_0, istogramma_bin_eta_1, ...] }
    L'ordine della lista segue l'ordine di ETA_BINS.
    """
    histos = {}
    for p in PT_BINS:
        histos[p["name"]] = []
        for e in ETA_BINS:
            h = ROOT.TH1F(
                f"h_res_{p['name']}_eta_{e['min']}_{e['max']}",
                "",
                100, -0.2, 0.2
            )
            histos[p["name"]].append(h)
    return histos
