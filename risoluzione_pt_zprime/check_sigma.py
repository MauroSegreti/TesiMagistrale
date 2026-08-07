"""
Diagnostica dell'estrazione della sigma.

Confronta, per ogni cella (eta, pT), stime diverse della larghezza:
  RMS          RMS dell'istogramma (sensibile alle code)
  g2.0 g2.5 g3.0   fit gaussiano iterativo entro +-N sigma dal core
  q68          semi-ampiezza dell'intervallo centrale che contiene il 68%
               (stimatore robusto: non assume nessuna forma)

Se le stime concordano, la sigma e' ben definita. Se divergono, la
distribuzione non e' gaussiana e il valore dipende dal metodo -- e allora
il numero da citare va scelto e motivato, non subito.

Salva anche i singoli istogrammi con il fit sovrapposto, per guardarli.

Uso:
    python3 check_sigma.py merged_res.root [indice_bin_eta]
"""

import os
import sys
import array

import ROOT
from config import PT_BINS, ETA_BINS
import style

style.apply_style()

IMAGES_DIR = "images/check_sigma"
N_SIGMA_LIST = [2.0, 2.5, 3.0]
MAX_ITER = 5
CONV_TOL = 1e-3


def fit_core(h, n_sigma):
    """Fit gaussiano iterativo entro +-n_sigma. Ritorna (sigma, sigma_err, TF1)."""
    mu = h.GetMean()
    sg = h.GetRMS()
    if sg <= 0 or h.GetEntries() < 50:
        return None, None, None

    best = None
    f = None
    for it in range(MAX_ITER):
        f = ROOT.TF1(f"g_{h.GetName()}_{n_sigma}_{it}", "gaus",
                     mu - n_sigma * sg, mu + n_sigma * sg)
        f.SetParameters(h.GetMaximum(), mu, sg)
        res = h.Fit(f, "QRNS")
        if not res.Get() or not res.IsValid():
            break
        mu_new, sg_new = f.GetParameter(1), f.GetParameter(2)
        if sg_new <= 0:
            break
        converged = abs(sg_new - sg) / sg < CONV_TOL
        mu, sg = mu_new, sg_new
        best = (f.GetParameter(2), f.GetParError(2), f)
        if converged:
            break
    if best is None:
        return None, None, None
    return best


def quantile_halfwidth(h, frac=0.68):
    """Semi-ampiezza dell'intervallo centrale che contiene 'frac' degli eventi."""
    if h.GetEntries() < 10:
        return None
    lo = (1.0 - frac) / 2.0
    probs = array.array('d', [lo, 1.0 - lo])
    q = array.array('d', [0.0, 0.0])
    n = h.GetQuantiles(2, q, probs)
    if n < 2:
        return None
    return (q[1] - q[0]) / 2.0


def outflow(h):
    n_in = h.Integral()
    n_out = h.GetBinContent(0) + h.GetBinContent(h.GetNbinsX() + 1)
    tot = n_in + n_out
    return n_out / tot if tot > 0 else 1.0


def analyse_eta_bin(f, e_i, save_plots=True):
    e = ETA_BINS[e_i]
    print(f"\n{'='*104}")
    print(f"eta bin {e_i}:  {e['min']} <= |eta| < {e['max']}")
    print('='*104)
    head = (f"{'bin pT':>12}{'entries':>11}{'outflow':>9}{'RMS':>10}"
            + "".join(f"{'g%.1f' % n:>10}" for n in N_SIGMA_LIST)
            + f"{'q68':>10}{'q68/g2.0':>10}")
    print(head)

    if save_plots:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        c = ROOT.TCanvas(f"c_check_{e_i}", "", 1600, 1000)
        c.Divide(4, 4)

    keep = []
    for p_i, p in enumerate(PT_BINS):
        h = f.Get(f"h_res_eta_{e_i}_{p['name']}")
        if not h:
            continue
        n = int(h.GetEntries())
        if n == 0:
            print(f"{p['name']:>12}{n:>11}{'--':>9}{'--':>10}"
                  + "".join(f"{'--':>10}" for _ in N_SIGMA_LIST)
                  + f"{'--':>10}{'--':>10}")
            continue

        row = f"{p['name']:>12}{n:>11}{100*outflow(h):>8.1f}%{h.GetRMS():>10.4f}"

        sigmas = []
        fits = []
        for ns in N_SIGMA_LIST:
            s, s_err, fn = fit_core(h, ns)
            sigmas.append(s)
            fits.append(fn)
            row += f"{s:>10.4f}" if s else f"{'--':>10}"

        q = quantile_halfwidth(h)
        row += f"{q:>10.4f}" if q else f"{'--':>10}"
        if q and sigmas[0]:
            ratio = q / sigmas[0]
            flag = "  <--" if abs(ratio - 1) > 0.15 else ""
            row += f"{ratio:>10.2f}{flag}"
        print(row)

        if save_plots:
            c.cd(p_i + 1)
            ROOT.gPad.SetLogy()
            h.SetTitle(f"{p['name']} GeV")
            h.SetLineColor(ROOT.kBlack)
            h.Draw("HIST")
            for fn, col in zip(fits, (ROOT.kRed + 1, ROOT.kAzure + 2,
                                      ROOT.kGreen + 2)):
                if fn:
                    fn.SetLineColor(col)
                    fn.SetLineWidth(2)
                    fn.SetNpx(500)
                    fn.Draw("SAME")
                    keep.append(fn)
            keep.append(h)

    if save_plots:
        path = os.path.join(IMAGES_DIR, f"histos_eta{e_i}")
        c.SaveAs(f"{path}.png")
        print(f"\n[INFO] Istogrammi salvati in {path}.png")
        print("       (nero = dati, rosso = fit +-2.0s, blu = +-2.5s, verde = +-3.0s)")

    return keep


def main(merged, eta_index=None):
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    keep = []
    indices = [int(eta_index)] if eta_index is not None else range(len(ETA_BINS))
    for e_i in indices:
        keep.append(analyse_eta_bin(f, e_i))

    print("\nCome leggere la tabella:")
    print("  q68/g2.0 vicino a 1  -> il core e' gaussiano, la sigma e' ben definita")
    print("  q68/g2.0 molto > 1   -> code pesanti, il fit sul core sottostima la larghezza")
    print("  RMS >> g2.0          -> stessa cosa, vista dall'altro lato")
    print("  sigma che cresce con N_SIGMA -> il risultato dipende dalla finestra di fit\n")

    f.Close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 check_sigma.py merged_res.root [indice_bin_eta]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
