"""
Per ogni bin di pT costruisce il TGraphErrors di RMS vs |eta_truth|,
poi li disegna tutti sovrapposti in un unico canvas con lo stile
condiviso (style.py). La legenda è posizionata FUORI dall'area dati
(nel margine destro del canvas), così non copre mai le curve.

build_rms_graphs ritorna anche 'results': una lista di dict con tutti
i valori stampati a console, usata da report.py per generare la
tabella PDF.
"""

import os
import array
import ROOT
from config import PT_BINS, ETA_BINS
from style import PALETTE

IMAGES_DIR = "images"


def build_rms_graphs(histos):
    graphs = []
    results = []

    for i, p in enumerate(PT_BINS):
        x = array.array('d')
        y = array.array('d')
        ex = array.array('d')
        ey = array.array('d')

        print(f"\n=== pT bin {p['name']} ===")
        for e_i, e in enumerate(ETA_BINS):
            h = histos[p["name"]][e_i]
            rms = h.GetRMS()
            rms_err = h.GetRMSError()
            entries = int(h.GetEntries())
            print(f"  eta {e['min']}-{e['max']}: entries={entries}, RMS={rms:.4f}")

            x.append((e["min"] + e["max"]) / 2.0)
            ex.append((e["max"] - e["min"]) / 2.0)
            y.append(rms)
            ey.append(rms_err)

            results.append({
                "pt_name": p["name"], "pt_min": p["min"], "pt_max": p["max"],
                "eta_min": e["min"], "eta_max": e["max"],
                "entries": entries, "rms": rms, "rms_err": rms_err,
            })

        g = ROOT.TGraphErrors(len(x), x, y, ex, ey)
        g.SetName(f"g_{p['name']}")
        color = PALETTE[i % len(PALETTE)]
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.SetMarkerStyle(20)
        g.SetLineWidth(2)
        g.SetMarkerSize(1.3)
        graphs.append(g)

    return graphs, results


def draw_rms_vs_eta(graphs):
    os.makedirs(IMAGES_DIR, exist_ok=True)

    c = ROOT.TCanvas("c_rms_vs_eta", "RMS vs eta", 1100, 700)
    c.SetGrid(1, 1)
    # Margine destro allargato: qui dentro va la legenda, FUORI dall'area
    # dove sono disegnate le curve, quindi non si sovrappone mai ai dati.
    c.SetRightMargin(0.30)

    all_y = [g.GetY()[i] for g in graphs for i in range(g.GetN())]
    ymin, ymax = min(all_y) * 0.8, max(all_y) * 1.15

    leg = ROOT.TLegend(0.72, 0.35, 0.985, 0.85)
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetTextFont(42)
    leg.SetTextSize(0.032)

    for i, (p, g) in enumerate(zip(PT_BINS, graphs)):
        g.SetTitle("")
        g.GetXaxis().SetTitle("|#eta^{truth}|")
        g.GetYaxis().SetTitle("RMS della risoluzione in p_{T}")
        if i == 0:
            g.Draw("APL")
            g.GetYaxis().SetRangeUser(ymin, ymax)
        else:
            g.Draw("PL SAME")
        leg.AddEntry(g, f"p_{{T}} = {p['min']}-{p['max']} GeV", "lp")

    leg.Draw()

    path = os.path.join(IMAGES_DIR, "plot_RMS_vs_eta")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    return c
