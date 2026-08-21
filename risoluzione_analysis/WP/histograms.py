import array
import ROOT
from config import PT_BINS, ETA_RANGE, ETA_NBINS, PHI_RANGE, PHI_NBINS, WP_LIST


def make_resolution_histo(name, title):
    h = ROOT.TH1F(
        name,
        f"{title};"
        "(1/p_{T}^{reco} - 1/p_{T}^{truth})/(1/p_{T}^{truth});Events",
        100, -0.2, 0.2
    )
    h.SetLineWidth(2)
    h.SetDirectory(0)
    return h


def _pt_bin_edges():
    edges = [PT_BINS[0]["min"]] + [b["max"] for b in PT_BINS]
    return array.array('d', edges)


def make_eff_histo_pt(name, title):
    edges = _pt_bin_edges()
    h = ROOT.TH1F(name, f"{title};p_{{T}}^{{truth}} [GeV];Muons",
                  len(edges) - 1, edges)
    h.SetDirectory(0)
    return h


def make_eff_histo_uniform(name, title, nbins, xrange, xaxis_title):
    h = ROOT.TH1F(name, f"{title};{xaxis_title};Muons",
                  nbins, xrange[0], xrange[1])
    h.SetDirectory(0)
    return h


# per ogni variabile: come costruire il suo istogramma pass/total e con
# quale titolo per l'asse x
_EFF_VARS = {
    "pt": lambda name, title: make_eff_histo_pt(name, title),
    "eta": lambda name, title: make_eff_histo_uniform(
        name, title, ETA_NBINS, ETA_RANGE, "#eta^{truth}"),
    "phi": lambda name, title: make_eff_histo_uniform(
        name, title, PHI_NBINS, PHI_RANGE, "#phi^{truth} [rad]"),
}


def build_histogram_set():
    """Un istogramma di risoluzione per WP, piu' denominatore/numeratori
    condivisi in pT, eta, phi per il calcolo delle efficienze."""
    histos_res = {}
    eff_histos = {var: {} for var in _EFF_VARS}
    h_total = {}

    for var, make in _EFF_VARS.items():
        h_total[var] = make(f"h_total_{var}", "Reconstructed, truth-matched")

    for wp in WP_LIST:
        histos_res[wp] = make_resolution_histo(f"h_res_{wp}", f"Inclusive ({wp})")
        for var, make in _EFF_VARS.items():
            eff_histos[var][wp] = make(f"h_pass_{var}_{wp}", f"Passing {wp}")

    return histos_res, eff_histos, h_total
