"""
Fabbrica degli istogrammi usati dall'analisi.
Tenuto separato dal loop eventi: qui ci sono solo "definizioni",
il riempimento avviene in event_loop.py.
"""

import ROOT
from config import PT_BINS


def make_resolution_histo(name, title_prefix):
    h = ROOT.TH1F(
        name,
        f"{title_prefix};"
        "(1/p_{T}^{reco} - 1/p_{T}^{truth})/(1/p_{T}^{truth});Events",
        100, -0.2, 0.2
    )
    h.SetLineColor(ROOT.kBlue)
    h.SetLineWidth(2)
    return h


def build_histogram_set(suffix=""):
    """
    Crea il set completo di istogrammi: uno inclusivo + uno per ciascun
    bin di pT definito in config.PT_BINS.

    'suffix' distingue le versioni parallele, es. "" per l'inclusivo
    e "_prompt" per la selezione truthmuon_IFFType == 4 richiesta da Luca.
    """
    label = f" ({suffix.strip('_')})" if suffix else ""
    h_all = make_resolution_histo(f"h_res_all{suffix}", f"Inclusive{label}")

    histos_pt = {}
    for b in PT_BINS:
        name = f"h_res_{b['name']}{suffix}"
        title = f"{b['min']}-{b['max']} GeV{label}"
        histos_pt[b["name"]] = make_resolution_histo(name, title)

    return h_all, histos_pt
