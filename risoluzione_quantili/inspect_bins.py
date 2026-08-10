"""
Guarda i singoli punti prima di fittarli -- la prima cosa che ha chiesto Luca.

Per ogni cella (eta, pT) stampa:
  entries, outflow
  RMS
  gaus     sigma del fit gaussiano entro +-2 sigma
  q68      (q84 - q16)/2  [stimatore usato per il risultato]
  q68/gaus quanto i due metodi divergono
  asym     asimmetria: [(q84-med) - (med-q16)] / (q84-q16)
           0 = simmetrica, |asym| > 0.10 = coda marcata da un lato

E salva una griglia con gli istogrammi, la gaussiana sovrapposta e le linee
verticali a q16 / mediana / q84, per giudicare a occhio quanto sono gaussiani.

Uso:
    python3 inspect_bins.py merged_res.root [indice_bin_eta]
"""

import os
import sys

import ROOT

from config import PT_BINS, ETA_BINS
from resolution import sigma_q68, sigma_gaus, outflow_fraction, MIN_ENTRIES
from logtee import Tee
import style

style.apply_style()

IMAGES_DIR = "images/inspect"


def analyse(f, e_i, save_plots=True):
    e = ETA_BINS[e_i]
    print(f"\n{'='*100}")
    print(f"eta bin {e_i}:  {e['min']} <= |eta| < {e['max']}")
    print('='*100)
    print(f"{'bin pT':>12}{'entries':>11}{'outflow':>9}{'RMS':>10}"
          f"{'gaus':>10}{'q68':>10}{'q68/gaus':>10}{'asym':>9}")

    keep = []
    if save_plots:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        n = len(PT_BINS)
        ncol = 4
        nrow = (n + ncol - 1) // ncol
        c = ROOT.TCanvas(f"c_inspect_{e_i}", "", 400 * ncol, 300 * nrow)
        c.Divide(ncol, nrow)

    for p_i, p in enumerate(PT_BINS):
        h = f.Get(f"h_res_eta_{e_i}_{p['name']}")
        if not h:
            continue
        n_ent = int(h.GetEntries())
        if n_ent < MIN_ENTRIES:
            print(f"{p['name']:>12}{n_ent:>11}"
                  + "".join(f"{'--':>10}" for _ in range(4))
                  + f"{'--':>10}{'--':>9}")
            continue

        q = sigma_q68(h)
        g = sigma_gaus(h)

        row = (f"{p['name']:>12}{n_ent:>11}{100*outflow_fraction(h):>8.1f}%"
               f"{h.GetRMS():>10.4f}")
        row += f"{g['sigma']:>10.4f}" if g else f"{'--':>10}"
        row += f"{q['sigma']:>10.4f}" if q else f"{'--':>10}"
        if q and g and g["sigma"] > 0:
            ratio = q["sigma"] / g["sigma"]
            row += f"{ratio:>10.2f}"
        else:
            row += f"{'--':>10}"
        if q:
            flag = " *" if abs(q["asym"]) > 0.10 else ""
            row += f"{q['asym']:>+9.3f}{flag}"
        print(row)

        if save_plots:
            c.cd(p_i + 1)
            ROOT.gPad.SetLogy()
            h.SetTitle(f"{p['name']} GeV")
            h.SetLineColor(ROOT.kBlack)
            h.Draw("HIST")
            keep.append(h)

            if g:
                fn = ROOT.TF1(f"fv_{e_i}_{p_i}", "gaus",
                              g["mu"] - 4 * g["sigma"],
                              g["mu"] + 4 * g["sigma"])
                fn.SetParameters(h.GetMaximum(), g["mu"], g["sigma"])
                fn.SetLineColor(ROOT.kRed + 1)
                fn.SetLineWidth(2)
                fn.SetNpx(400)
                fn.Draw("SAME")
                keep.append(fn)

            if q:
                y_hi = h.GetMaximum()
                for val, col, sty in ((q["q16"], ROOT.kAzure + 2, 2),
                                      (q["mu"], ROOT.kGreen + 2, 1),
                                      (q["q84"], ROOT.kAzure + 2, 2)):
                    ln = ROOT.TLine(val, 0.5, val, y_hi)
                    ln.SetLineColor(col)
                    ln.SetLineStyle(sty)
                    ln.SetLineWidth(2)
                    ln.Draw()
                    keep.append(ln)

    if save_plots:
        path = os.path.join(IMAGES_DIR, f"histos_eta{e_i}")
        c.SaveAs(f"{path}.png")
        print(f"\n[INFO] Istogrammi in {path}.png")
        print("       nero = dati, rosso = gaussiana del core,")
        print("       verde = mediana, blu tratteggiato = q16 e q84")
        keep.append(c)

    return keep


def main(merged, eta_index=None):
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    keep = []
    indices = [int(eta_index)] if eta_index is not None else range(len(ETA_BINS))
    for e_i in indices:
        keep.append(analyse(f, e_i))

    print("\nCome leggere:")
    print("  q68/gaus ~ 1        -> la distribuzione e' gaussiana, i due metodi coincidono")
    print("  q68/gaus > 1.1      -> code pesanti, il fit sul core sottostima")
    print("  |asym| > 0.10       -> distribuzione asimmetrica, la gaussiana non e' adatta")
    print("  RMS >> q68          -> code molto lunghe (l'RMS non e' uno stimatore utile)\n")

    f.Close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 inspect_bins.py merged_res.root [indice_bin_eta]")
        sys.exit(1)
    tag = sys.argv[2] if len(sys.argv) > 2 else "tutti"
    with Tee(os.path.join(IMAGES_DIR, f"log_inspect_eta{tag}.txt")):
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
