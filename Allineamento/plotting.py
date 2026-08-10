import os
import array
import ROOT
from config import PLOT_X_MIN, PLOT_X_MAX

IMAGES_DIR = "images"


def _residual_graph(g):
    gr, f = g["graph"], g["fit"]
    x = array.array('d')
    y = array.array('d')
    ex = array.array('d')
    ey = array.array('d')
    for i in range(gr.GetN()):
        xi, yi = gr.GetX()[i], gr.GetY()[i]
        fi = f.Eval(xi)
        if fi <= 0:
            continue
        x.append(xi)
        y.append((yi - fi) / fi)
        ex.append(0.0)
        ey.append(gr.GetEY()[i] / fi)
    res = ROOT.TGraphErrors(len(x), x, y, ex, ey)
    res.SetMarkerStyle(20)
    res.SetMarkerSize(0.9)
    res.SetMarkerColor(gr.GetMarkerColor())
    res.SetLineColor(gr.GetLineColor())
    return res


def draw_resolution_vs_pt(graphs, filename="plot_res_vs_pt",
                          x_min=PLOT_X_MIN, x_max=PLOT_X_MAX,
                          subtitle=""):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    keep = []

    c = ROOT.TCanvas(f"c_{filename}", "pT Resolution", 1150, 900)

    pad1 = ROOT.TPad(f"p1_{filename}", "", 0.0, 0.30, 1.0, 1.0)
    pad2 = ROOT.TPad(f"p2_{filename}", "", 0.0, 0.0, 1.0, 0.30)
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

    pad1.cd()
    all_y = [g["graph"].GetY()[i]
             for g in graphs for i in range(g["graph"].GetN())]
    y_min = max(min(all_y) * 0.5, 1e-4)
    y_max = max(all_y) * 2.0

    frame = ROOT.TH2F(f"fr_{filename}", ";;#sigma_{68}(p_{T})/p_{T}",
                      100, x_min, x_max, 100, y_min, y_max)
    frame.GetYaxis().SetTitleSize(0.045)
    frame.GetYaxis().SetTitleOffset(1.1)
    frame.GetYaxis().SetLabelSize(0.040)
    frame.GetXaxis().SetLabelSize(0)
    frame.Draw()
    keep.append(frame)

    for g in graphs:
        g["fit"].SetRange(g["x_lo"], g["x_hi"])
        g["fit"].Draw("SAME")
    for g in graphs:
        g["graph"].Draw("P SAME")

    if subtitle:
        # nel margine superiore, sopra la cornice: a y < 0.90 finiva
        # sovrapposto alla riga alta del riquadro
        lat = ROOT.TLatex()
        lat.SetNDC()
        lat.SetTextFont(42)
        lat.SetTextSize(0.040)
        lat.SetTextAlign(11)
        lat.DrawLatex(0.11, 0.935, subtitle)
        keep.append(lat)

    leg = ROOT.TLegend(0.735, 0.08, 0.985, 0.52)
    leg.SetHeader("#eta Range")
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetTextSize(0.034)
    for g in graphs:
        leg.AddEntry(g["graph"], g["eta"]["label"], "lp")
    leg.Draw()
    keep.append(leg)

    box = ROOT.TPaveText(0.735, 0.58, 0.985, 0.95, "NDC")
    box.SetBorderSize(1)
    box.SetFillColor(ROOT.kWhite)
    box.SetTextSize(0.038)
    box.SetTextAlign(22)
    box.AddText("#frac{#sigma_{p_{T}}}{p_{T}} =")
    box.AddText("#sqrt{#frac{r_{0}^{2}}{p_{T}^{2}} + r_{1}^{2} + (r_{2} #times p_{T})^{2}}")
    box.Draw()
    keep.append(box)

    pad2.cd()
    residuals = [_residual_graph(g) for g in graphs]
    keep += residuals
    r_all = [r.GetY()[i] for r in residuals for i in range(r.GetN())]
    r_lim = max(0.05, min(1.0, max(abs(v) for v in r_all) * 1.2)) if r_all else 0.5

    frame2 = ROOT.TH2F(f"fr2_{filename}",
                       ";p_{T}^{truth} [GeV];#frac{dato - fit}{fit}",
                       100, x_min, x_max, 100, -r_lim, r_lim)
    frame2.GetXaxis().SetTitleSize(0.105)
    frame2.GetXaxis().SetTitleOffset(1.25)
    frame2.GetXaxis().SetLabelSize(0.095)
    frame2.GetYaxis().SetTitleSize(0.090)
    frame2.GetYaxis().SetTitleOffset(0.45)
    frame2.GetYaxis().SetLabelSize(0.085)
    frame2.GetYaxis().SetNdivisions(505)
    frame2.Draw()
    keep.append(frame2)

    zero = ROOT.TLine(x_min, 0.0, x_max, 0.0)
    zero.SetLineStyle(2)
    zero.SetLineWidth(2)
    zero.Draw()
    keep.append(zero)

    for r in residuals:
        r.Draw("P SAME")

    path = os.path.join(IMAGES_DIR, filename)
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"[INFO] Salvato: {path}.png / .pdf")
    return c, keep


def draw_estimator_comparison(graphs_q68, graphs_gaus,
                              filename="plot_confronto_stimatori"):
    """Sovrappone i punti q68 (pieni) e gaussiani (vuoti), senza fit."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    keep = []

    c = ROOT.TCanvas(f"c_{filename}", "q68 vs gaus", 1150, 750)
    c.SetLogx()
    c.SetLogy()
    c.SetGrid()
    c.SetRightMargin(0.28)
    c.SetLeftMargin(0.11)

    all_y = [g["graph"].GetY()[i]
             for g in graphs_q68 + graphs_gaus
             for i in range(g["graph"].GetN())]
    frame = ROOT.TH2F(f"fr_{filename}",
                      ";p_{T}^{truth} [GeV];#sigma(p_{T})/p_{T}",
                      100, PLOT_X_MIN, PLOT_X_MAX,
                      100, max(min(all_y) * 0.5, 1e-4), max(all_y) * 2.0)
    frame.Draw()
    keep.append(frame)

    leg = ROOT.TLegend(0.735, 0.12, 0.985, 0.88)
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetTextSize(0.026)

    for g in graphs_q68:
        g["graph"].SetMarkerStyle(20)
        g["graph"].Draw("P SAME")
        leg.AddEntry(g["graph"], f"{g['eta']['label']}  q68", "p")
    for g in graphs_gaus:
        g["graph"].SetMarkerStyle(24)
        g["graph"].Draw("P SAME")
        leg.AddEntry(g["graph"], f"{g['eta']['label']}  gaus", "p")

    leg.Draw()
    keep.append(leg)

    path = os.path.join(IMAGES_DIR, filename)
    c.SaveAs(f"{path}.png")
    print(f"[INFO] Salvato: {path}.png")
    return c, keep


def print_fit_parameters(graphs):
    print("\n=== Parametri del fit per bin di eta ===")
    for g in graphs:
        for label, f in (("r0 libero ", g["fit"]), ("r0 = 0    ", g["fit_fixed0"])):
            ndf = f.GetNDF()
            chi2ndf = f.GetChisquare() / ndf if ndf > 0 else float("nan")
            print(
                f"  {g['eta']['label']:>24} [{label}] "
                f"r0={f.GetParameter(0):7.3f}+-{f.GetParError(0):6.3f}  "
                f"r1={f.GetParameter(1):.4f}+-{f.GetParError(1):.4f}  "
                f"r2={f.GetParameter(2)*1e3:.4f}+-{f.GetParError(2)*1e3:.4f} x10^-3 GeV^-1  "
                f"chi2/ndf={chi2ndf:.2f}"
            )
        print()
