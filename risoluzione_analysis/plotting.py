"""
Tutto ciò che riguarda disegno e salvataggio dei plot:
- il grafico RMS vs pT
- l'istogramma inclusivo con legenda
- l'overlay di tutti i bin di pT in un unico canvas (più leggibile
  di 7 PNG separati per confrontare le forme delle distribuzioni)

Usa lo stile definito in style.py: chiama style.apply_style() una
volta sola in main.py prima di creare qualsiasi canvas.
"""

import os
import ROOT
from config import PT_BINS
from style import PALETTE, style_histo, make_legend

IMAGES_DIR = "images"


def make_rms_graph(histos_pt, name, title):
    import array
    x = array.array('d')
    y = array.array('d')
    ex = array.array('d')
    ey = array.array('d')

    for b in PT_BINS:
        h = histos_pt[b["name"]]
        x.append(b["x_center"])
        ex.append(b["x_err"])
        y.append(h.GetRMS())
        ey.append(h.GetRMSError())

    graph = ROOT.TGraphErrors(len(x), x, y, ex, ey)
    graph.SetName(name)
    graph.SetTitle(title)
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.3)
    graph.SetMarkerColor(ROOT.kAzure + 2)
    graph.SetLineColor(ROOT.kAzure + 2)
    graph.SetLineWidth(2)
    return graph


def _save(canvas, basename):
    """Salva sia in PNG (per condividere/incollare) sia in PDF (vettoriale, per tesi/paper),
    dentro la sottocartella images/ (creata automaticamente se non esiste)."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    path = os.path.join(IMAGES_DIR, basename)
    canvas.SaveAs(f"{path}.png")
    canvas.SaveAs(f"{path}.pdf")


def draw_inclusive(h_all, suffix=""):
    c = ROOT.TCanvas(f"c_all{suffix}", "Inclusive", 900, 700)
    style_histo(h_all, ROOT.kAzure + 2, fill=True)
    h_all.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
    h_all.GetYaxis().SetTitle("Muoni / bin")
    h_all.Draw("HIST")

    leg = make_legend(0.60, 0.66, 0.90, 0.90)
    leg.AddEntry(h_all, "Inclusive", "f")
    leg.AddEntry(0, f"Entries = {int(h_all.GetEntries())}", "")
    leg.AddEntry(0, f"Mean = {h_all.GetMean():.4f}", "")
    leg.AddEntry(0, f"RMS = {h_all.GetRMS():.4f}", "")
    leg.Draw()

    _save(c, f"h_res_all{suffix}")
    return c


def draw_bins_overlay(histos_pt, suffix=""):
    """Sovrappone tutti i bin di pT in un unico canvas, colori distinti."""
    c = ROOT.TCanvas(f"c_bins_overlay{suffix}", "Bins overlay", 950, 700)

    # Normalizza ad area unitaria per confrontare le FORME, non i conteggi assoluti
    leg = make_legend(0.66, 0.55, 0.92, 0.90)
    y_max = 0
    for i, b in enumerate(PT_BINS):
        h = histos_pt[b["name"]]
        color = PALETTE[i % len(PALETTE)]
        style_histo(h, color)
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())
        y_max = max(y_max, h.GetMaximum())

    for i, b in enumerate(PT_BINS):
        h = histos_pt[b["name"]]
        h.SetMaximum(y_max * 1.35)
        h.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
        h.GetYaxis().SetTitle("Frazione di eventi / bin")
        h.Draw("HIST" if i == 0 else "HIST SAME")
        leg.AddEntry(h, f"{b['min']}-{b['max']} GeV", "l")

    leg.Draw()
    _save(c, f"plot_bins_overlay{suffix}")
    return c


def draw_single_bins(histos_pt, suffix=""):
    """Un PNG/PDF per bin, se ti servono ancora i plot singoli separati."""
    c = ROOT.TCanvas(f"c_bin{suffix}", "Bins", 900, 700)
    for i, b in enumerate(PT_BINS):
        h = histos_pt[b["name"]]
        color = PALETTE[i % len(PALETTE)]
        style_histo(h, color, fill=True)
        h.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
        h.GetYaxis().SetTitle("Muoni / bin")
        h.Draw("HIST")

        leg = make_legend()
        leg.AddEntry(h, f"{b['min']}-{b['max']} GeV", "f")
        leg.AddEntry(0, f"Entries = {int(h.GetEntries())}", "")
        leg.AddEntry(0, f"RMS = {h.GetRMS():.4f}", "")
        leg.Draw()

        _save(c, f"plot_range_{b['name']}{suffix}")


def draw_rms_graph(graph, suffix=""):
    c = ROOT.TCanvas(f"c_rms{suffix}", "RMS vs pT", 900, 700)
    c.SetGrid(1, 1)
    graph.GetXaxis().SetTitle("p_{T}^{truth} [GeV]")
    graph.GetYaxis().SetTitle("RMS")
    graph.Draw("AP")
    _save(c, f"rms_vs_pt{suffix}")
    return c


def save_all_plots(h_all, histos_pt, graph, suffix=""):
    draw_inclusive(h_all, suffix)
    draw_bins_overlay(histos_pt, suffix)
    draw_single_bins(histos_pt, suffix)
    draw_rms_graph(graph, suffix)