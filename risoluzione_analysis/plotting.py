import os
import array
import ROOT
from config import PT_BINS, IMAGES_DIR
from style import PALETTE, style_histo, make_legend


def make_rms_graph(histos_pt, name, title):
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
    os.makedirs(IMAGES_DIR, exist_ok=True)
    path = os.path.join(IMAGES_DIR, basename)
    canvas.SaveAs(f"{path}.png")
    canvas.SaveAs(f"{path}.pdf")


def draw_inclusive(h_all, suffix=""):
    c = ROOT.TCanvas(f"c_all{suffix}", "Inclusive", 900, 700)
    style_histo(h_all, ROOT.kAzure + 2, fill=True)
    h_all.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
    h_all.GetYaxis().SetTitle("Muons / bin")
    h_all.Draw("HIST")

    leg = make_legend(0.60, 0.66, 0.90, 0.90)
    leg.AddEntry(h_all, "Inclusive", "f")
    leg.AddEntry(0, f"Entries = {int(h_all.GetEntries())}", "")
    leg.AddEntry(0, f"Mean = {h_all.GetMean():.4f}", "")
    leg.AddEntry(0, f"RMS = {h_all.GetRMS():.4f}", "")
    leg.Draw()

    _save(c, f"h_res_all{suffix}")
    return c


def draw_single_bins(histos_pt, suffix=""):
    c = ROOT.TCanvas(f"c_bin{suffix}", "Bins", 900, 700)
    for i, b in enumerate(PT_BINS):
        h = histos_pt[b["name"]]
        color = PALETTE[i % len(PALETTE)]
        style_histo(h, color, fill=True)
        h.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
        h.GetYaxis().SetTitle("Muons / bin")
        h.Draw("HIST")

        leg = make_legend()
        leg.AddEntry(h, f"{b['min']}-{b['max']} GeV", "f")
        leg.AddEntry(0, f"Entries = {int(h.GetEntries())}", "")
        leg.AddEntry(0, f"RMS = {h.GetRMS():.4f}", "")
        leg.Draw()

        _save(c, f"plot_range_{b['name']}{suffix}")


def draw_bins_overlay(histos_pt, suffix=""):
    c = ROOT.TCanvas(f"c_bins_overlay{suffix}", "Bins overlay", 950, 700)
    leg = make_legend(0.66, 0.55, 0.92, 0.90)

    clones = []
    y_max = 0.0
    for i, b in enumerate(PT_BINS):
        h = histos_pt[b["name"]].Clone(f"{histos_pt[b['name']].GetName()}_norm")
        h.SetDirectory(0)
        style_histo(h, PALETTE[i % len(PALETTE)])
        h.SetFillStyle(0)
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())
        y_max = max(y_max, h.GetMaximum())
        clones.append(h)

    for i, (b, h) in enumerate(zip(PT_BINS, clones)):
        h.SetMaximum(y_max * 1.35)
        h.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
        h.GetYaxis().SetTitle("Fraction of events / bin")
        h.Draw("HIST" if i == 0 else "HIST SAME")
        leg.AddEntry(h, f"{b['min']}-{b['max']} GeV", "l")

    leg.Draw()
    _save(c, f"plot_bins_overlay{suffix}")
    return c, clones


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
    draw_single_bins(histos_pt, suffix)
    draw_bins_overlay(histos_pt, suffix)
    draw_rms_graph(graph, suffix)
