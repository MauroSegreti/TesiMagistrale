"""
Guarda i singoli punti prima di fittarli.

Stampa per ogni cella (eta, pT):
  entries, outflow
  RMS
  gaus      sigma del fit gaussiano entro +-2 sigma dal core
  chi2/ndf  del fit gaussiano (con 10^7 entries e' enorme anche per
            deviazioni minime: leggilo insieme a ndf e alle entries)
  q68       (q84 - q16)/2  [stimatore usato per il risultato]
  q68/gaus  quanto i due metodi divergono
  RMS/q68   lunghezza delle code
  code%     frazione di eventi oltre +-2 sigma dal core
            (una gaussiana ne ha il 4.55%: quanto sopra, tanto e' l'eccesso)
  asym      [(q84-med) - (med-q16)] / (q84-q16)

Salva due griglie di istogrammi per ogni bin di eta:
  histos_etaN_lin.png   scala lineare, zoomata sul core -> si giudica se la
                        gaussiana prende il PICCO
  histos_etaN_log.png   scala log, finestra intera -> si vedono le code

NB: la variabile pT_truth/pT_reco - 1 e' intrinsecamente asimmetrica.
Ha un limite fisico a -1 (pT_reco -> infinito) ed e' illimitata a destra
(pT_reco -> 0). La coda destra sono muoni con pT sottostimato: irraggiamento,
perdita di energia, misure sbagliate.

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

N_SIGMA_TAIL = 2.0     # soglia per la frazione nelle code
GAUS_TAIL_FRAC = 4.55  # % attesa oltre +-2 sigma per una gaussiana
ZOOM_N_SIGMA = 5.0     # zoom della versione lineare


def tail_fraction(h, mu, sigma, n_sigma=N_SIGMA_TAIL):
    """% di eventi oltre +-n_sigma dal centro del core."""
    tot = h.Integral(0, h.GetNbinsX() + 1)
    if tot <= 0:
        return None
    lo = h.FindBin(mu - n_sigma * sigma)
    hi = h.FindBin(mu + n_sigma * sigma)
    dentro = h.Integral(lo, hi)
    return 100.0 * (tot - dentro) / tot


def _draw_grid(f, e_i, logy, zoom, suffix):
    n = len(PT_BINS)
    ncol = 4
    nrow = (n + ncol - 1) // ncol
    c = ROOT.TCanvas(f"c_insp_{e_i}_{suffix}", "", 400 * ncol, 300 * nrow)
    c.Divide(ncol, nrow)
    keep = [c]

    for p_i, p in enumerate(PT_BINS):
        h0 = f.Get(f"h_res_eta_{e_i}_{p['name']}")
        if not h0 or h0.GetEntries() < MIN_ENTRIES:
            continue
        h = h0.Clone(f"{h0.GetName()}_{suffix}")
        h.SetDirectory(0)

        g = sigma_gaus(h)
        q = sigma_q68(h)

        c.cd(p_i + 1)
        if logy:
            ROOT.gPad.SetLogy()

        if zoom and g:
            h.GetXaxis().SetRangeUser(g["mu"] - ZOOM_N_SIGMA * g["sigma"],
                                      g["mu"] + ZOOM_N_SIGMA * g["sigma"])

        h.SetTitle(f"{p['name']} GeV")
        h.SetLineColor(ROOT.kBlack)
        h.Draw("HIST")
        keep.append(h)

        if g:
            fn = ROOT.TF1(f"fn_{e_i}_{p_i}_{suffix}", "gaus",
                          g["mu"] - 6 * g["sigma"], g["mu"] + 6 * g["sigma"])
            fn.SetParameters(h.GetMaximum(), g["mu"], g["sigma"])
            fn.SetLineColor(ROOT.kRed + 1)
            fn.SetLineWidth(2)
            fn.SetNpx(500)
            fn.Draw("SAME")
            keep.append(fn)

        if q:
            y_hi = h.GetMaximum()
            y_lo = 0.5 if logy else 0.0
            for val, col, sty in ((q["q16"], ROOT.kAzure + 2, 2),
                                  (q["mu"], ROOT.kGreen + 2, 1),
                                  (q["q84"], ROOT.kAzure + 2, 2)):
                ln = ROOT.TLine(val, y_lo, val, y_hi)
                ln.SetLineColor(col)
                ln.SetLineStyle(sty)
                ln.SetLineWidth(2)
                ln.Draw()
                keep.append(ln)

    path = os.path.join(IMAGES_DIR, f"histos_eta{e_i}_{suffix}")
    c.SaveAs(f"{path}.png")
    print(f"[INFO] {path}.png")
    return keep


def analyse(f, e_i, save_plots=True):
    e = ETA_BINS[e_i]
    print(f"\n{'='*126}")
    print(f"eta bin {e_i}:  {e['min']} <= |eta| < {e['max']}")
    print('='*126)
    print(f"{'bin pT':>12}{'entries':>11}{'outflow':>9}{'RMS':>10}"
          f"{'gaus':>10}{'chi2/ndf':>11}{'ndf':>6}"
          f"{'q68':>10}{'q68/gaus':>10}{'RMS/q68':>9}{'code%':>8}{'asym':>9}")

    for p_i, p in enumerate(PT_BINS):
        h = f.Get(f"h_res_eta_{e_i}_{p['name']}")
        if not h:
            continue
        n_ent = int(h.GetEntries())
        if n_ent < MIN_ENTRIES:
            print(f"{p['name']:>12}{n_ent:>11}"
                  + "".join(f"{'--':>10}" for _ in range(8)))
            continue

        q = sigma_q68(h)
        g = sigma_gaus(h)

        row = (f"{p['name']:>12}{n_ent:>11}{100*outflow_fraction(h):>8.1f}%"
               f"{h.GetRMS():>10.4f}")
        if g:
            row += f"{g['sigma']:>10.4f}{g['chi2ndf']:>11.1f}{g['ndf']:>6d}"
        else:
            row += f"{'--':>10}{'--':>11}{'--':>6}"
        row += f"{q['sigma']:>10.4f}" if q else f"{'--':>10}"
        row += (f"{q['sigma']/g['sigma']:>10.2f}"
                if (q and g and g["sigma"] > 0) else f"{'--':>10}")
        row += f"{h.GetRMS()/q['sigma']:>9.2f}" if q else f"{'--':>9}"
        if g:
            t = tail_fraction(h, g["mu"], g["sigma"])
            row += f"{t:>8.1f}" if t is not None else f"{'--':>8}"
        else:
            row += f"{'--':>8}"
        if q:
            flag = " *" if abs(q["asym"]) > 0.10 else ""
            row += f"{q['asym']:>+9.3f}{flag}"
        print(row)

    keep = []
    if save_plots:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        print()
        keep.append(_draw_grid(f, e_i, logy=False, zoom=True, suffix="lin"))
        keep.append(_draw_grid(f, e_i, logy=True, zoom=False, suffix="log"))
        print("       nero = dati, rosso = gaussiana del core,")
        print("       verde = mediana, blu tratteggiato = q16 e q84")
        print("       _lin: lineare, zoom sul core -> la gaussiana prende il picco?")
        print("       _log: log, finestra intera -> quanto sono lunghe le code")
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
    print("  q68/gaus ~ 1   -> distribuzione gaussiana, i due metodi coincidono")
    print("  q68/gaus > 1.1 -> code pesanti, il fit sul core sottostima")
    print("  RMS/q68 ~ 1    -> niente code; cresce se le code si allungano")
    print(f"  code%          -> % oltre +-{N_SIGMA_TAIL:.0f} sigma. Una gaussiana"
          f" ne ha {GAUS_TAIL_FRAC}%:")
    print("                    l'eccesso rispetto a quel valore sono le code vere")
    print("  |asym| > 0.10  -> asimmetrica. NB: la variabile lo e' per costruzione,")
    print("                    ha un limite a -1 ed e' illimitata a destra")
    print("  chi2/ndf       -> del fit gaussiano. Con 10^7 entries e' enorme anche")
    print("                    per deviazioni minime, e la gaussiana non descrive")
    print("                    le code per definizione: guarda il picco nel _lin\n")

    f.Close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 inspect_bins.py merged_res.root [indice_bin_eta]")
        sys.exit(1)
    tag = sys.argv[2] if len(sys.argv) > 2 else "tutti"
    with Tee(os.path.join(IMAGES_DIR, f"log_inspect_eta{tag}.txt")):
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
