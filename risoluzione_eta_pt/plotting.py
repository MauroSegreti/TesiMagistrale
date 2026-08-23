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
from style import PALETTE, style_histo, make_legend

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


def draw_eta_overlay(histos):
    """
    Un solo canvas, inclusivo su tutti i bin di pT: per ogni bin di |eta|
    somma gli istogrammi di risoluzione sui 6 bin di pT, normalizza e
    sovrappone il risultato -- stesso schema di draw_bins_overlay in
    risoluzione_analysis, ma con l'eta al posto del pT. Solo muoni truth
    prompt (histos li contiene gia' solo prompt, vedi event_loop.py).
    """
    os.makedirs(IMAGES_DIR, exist_ok=True)

    c = ROOT.TCanvas("c_eta_overlay", "Eta overlay (inclusive in pT)", 950, 700)
    leg = make_legend(0.66, 0.55, 0.92, 0.90)

    clones = []
    y_max = 0.0
    for e_i, e in enumerate(ETA_BINS):
        h = histos[PT_BINS[0]["name"]][e_i].Clone(f"h_res_eta_{e['min']}_{e['max']}_incl")
        h.SetDirectory(0)
        for p in PT_BINS[1:]:
            h.Add(histos[p["name"]][e_i])
        style_histo(h, PALETTE[e_i % len(PALETTE)])
        h.SetFillStyle(0)
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())
        y_max = max(y_max, h.GetMaximum())
        clones.append(h)

    for e_i, (e, h) in enumerate(zip(ETA_BINS, clones)):
        h.SetMaximum(y_max * 1.35)
        h.GetXaxis().SetTitle("(p_{T}^{truth}/p_{T}^{reco}) - 1")
        h.GetYaxis().SetTitle("Fraction of muons / bin")
        h.Draw("HIST" if e_i == 0 else "HIST SAME")
        leg.AddEntry(h, f"|#eta| #in [{e['min']:.2f}, {e['max']:.2f})", "l")

    leg.Draw()

    path = os.path.join(IMAGES_DIR, "plot_eta_overlay")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    return c, clones


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
        g.GetYaxis().SetTitle("p_{T} resolution RMS")
        if i == 0:
            g.Draw("AP")
            g.GetYaxis().SetRangeUser(ymin, ymax)
        else:
            g.Draw("P SAME")
        leg.AddEntry(g, f"p_{{T}} = {p['min']}-{p['max']} GeV", "p")

    leg.Draw()

    path = os.path.join(IMAGES_DIR, "plot_RMS_vs_eta")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    return c
