"""
Fabbrica della griglia di istogrammi N x M richiesta da Marco:
N = numero di bin in pT, M = numero di bin in eta.
Un istogramma per ogni combinazione (bin pT, bin eta).
"""

import ROOT
from config import PT_BINS, ETA_BINS

# Range +-0.5 (non +-0.2): a pT alto le code della risoluzione superano
# facilmente 0.2 e finivano in overflow/underflow, esclusi di default dal
# calcolo di TH1::GetRMS() -- RMS sottostimata, in alcuni bin a statistica
# bassa addirittura 0. 250 bin per mantenere la stessa larghezza di bin
# (0.004) di quando il range era +-0.2 con 100 bin.
# Unica fonte di verita' sul binning: usato sia da build_histogram_grid
# sia da check_binning (nei merge_*.py) per validare gli output dei job
# prima di un hadd.
RES_NBINS, RES_XMIN, RES_XMAX = 250, -0.5, 0.5


def build_histogram_grid(pt_bins=None):
    """
    Ritorna un dict:
        { nome_bin_pt: [istogramma_bin_eta_0, istogramma_bin_eta_1, ...] }
    L'ordine della lista segue l'ordine di ETA_BINS. pt_bins di default e'
    config.PT_BINS, ma i moduli che estendono la griglia in pT (es.
    main_zzall.py) sovrascrivono il nome globale PT_BINS di questo modulo
    prima di chiamare la funzione.
    """
    if pt_bins is None:
        pt_bins = PT_BINS

    histos = {}
    for p in pt_bins:
        histos[p["name"]] = []
        for e in ETA_BINS:
            h = ROOT.TH1F(
                f"h_res_{p['name']}_eta_{e['min']}_{e['max']}",
                "",
                RES_NBINS, RES_XMIN, RES_XMAX
            )
            histos[p["name"]].append(h)
    return histos


def check_binning(files, pt_bins=None, eta_bins=None):
    """
    Controlla, prima di un hadd, che tutti i file abbiano il binning
    atteso (RES_NBINS, RES_XMIN, RES_XMAX) per un istogramma sonda
    (il primo bin di pT x il primo bin di eta). Senza questo controllo,
    un job rimasto con un output vecchio (es. ucciso da condor prima di
    sovrascrivere il file su EOS) fa fallire silenziosamente il merge di
    ROOT (TH1Merger::DifferentAxesMerge) e il totale delle entries
    risulta troncato senza errori evidenti -- e' successo con job_41 nel
    merge di ZZallRMS.
    """
    if pt_bins is None:
        pt_bins = PT_BINS
    if eta_bins is None:
        eta_bins = ETA_BINS

    probe_name = f"h_res_{pt_bins[0]['name']}_eta_{eta_bins[0]['min']}_{eta_bins[0]['max']}"

    bad = []
    for path in files:
        f = ROOT.TFile.Open(path)
        h = f.Get(probe_name)
        nb, xmin, xmax = h.GetNbinsX(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax()
        if (nb, xmin, xmax) != (RES_NBINS, RES_XMIN, RES_XMAX):
            bad.append((path, nb, xmin, xmax))
        f.Close()

    if bad:
        print(f"\n[ERROR] {len(bad)} file con binning diverso da quello atteso "
              f"({RES_NBINS}, {RES_XMIN}, {RES_XMAX}):")
        for path, nb, xmin, xmax in bad:
            print(f"  {path}: nbins={nb}, xmin={xmin}, xmax={xmax}")
        raise RuntimeError(
            "Binning incoerente tra i job -- probabile job rimasto con output "
            "vecchio (rilancialo e ripeti il merge prima di continuare)"
        )
