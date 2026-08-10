"""
Confronto diretto nominale (PerfectAlignment) vs MS-misaligned: stesso
identico binning/metodo/fit (vedi README), quindi la sola differenza fra le
due curve e' l'effetto del disallineamento.

Uso (da Disallineamento/, dopo aver girato analyze.py in entrambe le
cartelle cosi' esistono i due merged_res.root):
    python3 compare_alignment.py
"""

import os
import sys
import math
import array

import ROOT

ANADIR = os.path.dirname(os.path.abspath(__file__))
QUANTILI_DIR = os.path.join(os.path.dirname(ANADIR), "Allineamento")
sys.path.insert(0, QUANTILI_DIR)

from config import PT_BINS, ETA_BINS, PLOT_X_MIN, PLOT_X_MAX, PT_FIT_MAX
from histograms import read_pt_means
from fitting import build_graphs_and_fits
import style

style.apply_style()

IMAGES_DIR = os.path.join(ANADIR, "images")

NOMINAL_ROOT = os.path.join(QUANTILI_DIR, "merged_res.root")
MISALIGNED_ROOT = os.path.join(ANADIR, "merged_res.root")


def load(path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {path}")

    def grab(name):
        h = f.Get(name)
        if not h:
            raise RuntimeError(f"'{name}' non trovato in {path}")
        h = h.Clone()
        h.SetDirectory(0)
        return h

    histos = {e_i: [grab(f"h_res_eta_{e_i}_{p['name']}") for p in PT_BINS]
              for e_i in range(len(ETA_BINS))}
    h_sum, h_count = grab("h_pt_sum"), grab("h_pt_count")
    f.Close()

    pt_sums, pt_counts = read_pt_means(h_sum, h_count)
    return histos, pt_sums, pt_counts


def main():
    print(f"[INFO] Nominale:   {NOMINAL_ROOT}")
    print(f"[INFO] Misaligned: {MISALIGNED_ROOT}")

    histos_n, sums_n, counts_n = load(NOMINAL_ROOT)
    histos_m, sums_m, counts_m = load(MISALIGNED_ROOT)

    graphs_n = build_graphs_and_fits(histos_n, sums_n, counts_n,
                                     method="q68", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)
    graphs_m = build_graphs_and_fits(histos_m, sums_m, counts_m,
                                     method="q68", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)
    gm_by_eta = {g["eta_index"]: g for g in graphs_m}

    os.makedirs(IMAGES_DIR, exist_ok=True)
    keep = []

    c = ROOT.TCanvas("c_confronto_allineamento", "", 1150, 900)
    pad1 = ROOT.TPad("p1_align", "", 0.0, 0.30, 1.0, 1.0)
    pad2 = ROOT.TPad("p2_align", "", 0.0, 0.0, 1.0, 0.30)
    for p in (pad1, pad2):
        p.SetRightMargin(0.28)
        p.SetLeftMargin(0.11)
        p.SetLogx()
        p.SetGrid()
    pad1.SetBottomMargin(0.02)
    pad1.SetTopMargin(0.10)
    pad1.SetLogy()
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.32)
    pad1.Draw()
    pad2.Draw()
    keep += [pad1, pad2]

    # --- pannello superiore: punti + fit, nominale vs misaligned ---
    pad1.cd()
    all_y = [g["graph"].GetY()[i]
             for g in graphs_n + graphs_m for i in range(g["graph"].GetN())]
    y_min = max(min(all_y) * 0.5, 1e-4)
    y_max = max(all_y) * 2.0

    frame = ROOT.TH2F("fr_align", ";;#sigma_{68}(p_{T})/p_{T}",
                      100, PLOT_X_MIN, PLOT_X_MAX, 100, y_min, y_max)
    frame.GetYaxis().SetTitleSize(0.045)
    frame.GetYaxis().SetTitleOffset(1.1)
    frame.GetYaxis().SetLabelSize(0.040)
    frame.GetXaxis().SetLabelSize(0)
    frame.Draw()
    keep.append(frame)

    for g in graphs_n:
        g["graph"].SetMarkerStyle(20)   # pieno = nominale
        g["fit"].SetLineStyle(1)
        g["fit"].SetRange(g["x_lo"], g["x_hi"])
        g["fit"].Draw("SAME")
    for g in graphs_m:
        g["graph"].SetMarkerStyle(24)   # vuoto = misaligned
        g["fit"].SetLineStyle(2)
        g["fit"].SetRange(g["x_lo"], g["x_hi"])
        g["fit"].Draw("SAME")
    for g in graphs_n + graphs_m:
        g["graph"].Draw("P SAME")

    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextFont(42)
    lat.SetTextSize(0.036)
    lat.SetTextAlign(11)
    lat.DrawLatex(0.11, 0.935,
                  "pieno / linea continua = nominale   "
                  "vuoto / tratteggiata = misaligned")
    keep.append(lat)

    leg = ROOT.TLegend(0.735, 0.06, 0.985, 0.54)
    leg.SetHeader("#eta Range")
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetTextSize(0.030)
    for g in graphs_n:
        leg.AddEntry(g["graph"], g["eta"]["label"], "lp")
    leg.Draw()
    keep.append(leg)

    box = ROOT.TPaveText(0.735, 0.58, 0.985, 0.95, "NDC")
    box.SetBorderSize(1)
    box.SetFillColor(ROOT.kWhite)
    box.SetTextSize(0.032)
    box.SetTextAlign(22)
    box.AddText("#frac{#sigma_{p_{T}}}{p_{T}} =")
    box.AddText("#sqrt{#frac{r_{0}^{2}}{p_{T}^{2}} + r_{1}^{2} + (r_{2} #times p_{T})^{2}}")
    box.Draw()
    keep.append(box)

    # --- pannello inferiore: rapporto fra le due curve di fit ---
    pad2.cd()
    ratio_graphs = []
    for g_n in graphs_n:
        g_m = gm_by_eta.get(g_n["eta_index"])
        if g_m is None:
            continue
        lo = max(g_n["x_lo"], g_m["x_lo"])
        hi = min(g_n["x_hi"], g_m["x_hi"])
        if lo >= hi:
            continue
        log_lo, log_hi = math.log10(lo), math.log10(hi)
        xs, ys = array.array('d'), array.array('d')
        n_pts = 200
        for i in range(n_pts):
            x = 10 ** (log_lo + (log_hi - log_lo) * i / (n_pts - 1))
            fn = g_n["fit"].Eval(x)
            if fn <= 0:
                continue
            xs.append(x)
            ys.append(g_m["fit"].Eval(x) / fn)
        gr = ROOT.TGraph(len(xs), xs, ys)
        gr.SetLineColor(g_n["graph"].GetMarkerColor())
        gr.SetLineWidth(2)
        ratio_graphs.append(gr)
    keep += ratio_graphs

    r_all = [gr.GetY()[i] for gr in ratio_graphs for i in range(gr.GetN())]
    r_max = max(r_all) * 1.15 if r_all else 5.0

    frame2 = ROOT.TH2F("fr2_align",
                       ";p_{T}^{truth} [GeV];misaligned / nominale",
                       100, PLOT_X_MIN, PLOT_X_MAX, 100, 0.8, r_max)
    frame2.GetXaxis().SetTitleSize(0.105)
    frame2.GetXaxis().SetTitleOffset(1.25)
    frame2.GetXaxis().SetLabelSize(0.095)
    frame2.GetYaxis().SetTitleSize(0.075)
    frame2.GetYaxis().SetTitleOffset(0.55)
    frame2.GetYaxis().SetLabelSize(0.085)
    frame2.GetYaxis().SetNdivisions(505)
    frame2.Draw()
    keep.append(frame2)

    one = ROOT.TLine(PLOT_X_MIN, 1.0, PLOT_X_MAX, 1.0)
    one.SetLineStyle(2)
    one.SetLineWidth(2)
    one.Draw()
    keep.append(one)

    for gr in ratio_graphs:
        gr.Draw("L SAME")

    path = os.path.join(IMAGES_DIR, "plot_confronto_allineamento")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"[INFO] Salvato: {path}.png / .pdf")


if __name__ == "__main__":
    main()
