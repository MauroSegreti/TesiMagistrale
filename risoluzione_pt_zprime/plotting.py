import os
import array
import ROOT
from config import PLOT_X_MIN, PLOT_X_MAX

IMAGES_DIR = "images"


def _residual_graph(g):
    """(dato - fit) / fit punto per punto."""
    gr = g["graph"]
    f = g["fit"]
    x = array.array('d')
    y = array.array('d')
    ex = array.array('d')
    ey = array.array('d')
    for i in range(gr.GetN()):
        xi = gr.GetX()[i]
        yi = gr.GetY()[i]
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
                          x_min=PLOT_X_MIN, x_max=PLOT_X_MAX):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    keep = []

    c = ROOT.TCanvas(f"c_{filename}", "pT Resolution vs pT truth", 1150, 900)

    pad1 = ROOT.TPad(f"pad1_{filename}", "", 0.0, 0.30, 1.0, 1.0)
    pad2 = ROOT.TPad(f"pad2_{filename}", "", 0.0, 0.0, 1.0, 0.30)
    for p in (pad1, pad2):
        p.SetRightMargin(0.28)
        p.SetLeftMargin(0.11)
        p.SetLogx()
        p.SetGrid()
    pad1.SetBottomMargin(0.02)
    pad1.SetLogy()
    pad2.SetTopMargin(0.03)
    pad2.SetBottomMargin(0.32)
    pad1.Draw()
    pad2.Draw()
    keep += [pad1, pad2]

    # ------------------------------------------------ pad superiore
    pad1.cd()

    all_y = [g["graph"].GetY()[i]
             for g in graphs for i in range(g["graph"].GetN())]
    y_min = max(min(all_y) * 0.5, 1e-4)
    y_max = max(all_y) * 2.0

    frame = ROOT.TH2F(
        f"frame_{filename}", ";;#sigma(p_{T})/p_{T}",
        100, x_min, x_max, 100, y_min, y_max
    )
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

    formula_box = ROOT.TPaveText(0.735, 0.58, 0.985, 0.95, "NDC")
    formula_box.SetBorderSize(1)
    formula_box.SetFillColor(ROOT.kWhite)
    formula_box.SetTextSize(0.038)
    formula_box.SetTextAlign(22)
    formula_box.AddText("#frac{#sigma_{p_{T}}}{p_{T}} =")
    formula_box.AddText("#sqrt{#frac{r_{0}^{2}}{p_{T}^{2}} + r_{1}^{2} + (r_{2} #times p_{T})^{2}}")
    formula_box.Draw()
    keep.append(formula_box)

    # ------------------------------------------------ pad dei residui
    pad2.cd()

    residuals = [_residual_graph(g) for g in graphs]
    keep += residuals

    r_all = [r.GetY()[i] for r in residuals for i in range(r.GetN())]
    r_lim = max(0.05, min(1.0, max(abs(v) for v in r_all) * 1.2)) if r_all else 0.5

    frame2 = ROOT.TH2F(
        f"frame2_{filename}",
        ";p_{T}^{truth} [GeV];#frac{dato - fit}{fit}",
        100, x_min, x_max, 100, -r_lim, r_lim
    )
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
