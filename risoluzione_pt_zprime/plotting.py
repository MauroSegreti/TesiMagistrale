"""
Disegna il canvas finale: RMS della risoluzione in pT (asse x log)
vs pT truth, una curva per ogni bin di eta.

Legenda e formula sono posizionate FUORI dall'area dati (nel margine
destro del canvas, allargato apposta), cosi' non si sovrappongono mai
alle curve indipendentemente da dove finiscono i punti -- lo stesso
approccio usato in risoluzione_eta_pt.
"""

import os
import ROOT
from config import PLOT_X_MIN, PLOT_X_MAX

IMAGES_DIR = "images"


def draw_resolution_vs_pt(graphs, filename="plot_res_vs_pt_3TeV"):
    os.makedirs(IMAGES_DIR, exist_ok=True)

    c = ROOT.TCanvas("c_res_vs_pt", "pT Resolution vs pT truth", 1150, 750)
    c.SetGrid()
    c.SetLogx()
    c.SetRightMargin(0.28)  # spazio riservato a legenda + formula, fuori dai dati

    y_max = max(g["graph"].GetY()[i] for g in graphs for i in range(g["graph"].GetN())) * 1.25

    dummy = ROOT.TH2F(
        "dummy",
        "p_{T} Resolution vs p_{T}^{truth};p_{T}^{truth} [GeV];RMS",
        100, PLOT_X_MIN, PLOT_X_MAX, 100, 0, y_max
    )
    dummy.Draw()

    for g in graphs:
        g["graph"].Draw("P SAME")
        g["fit"].Draw("SAME")

    # Legenda nel margine destro (fuori dall'area dati)
    leg = ROOT.TLegend(0.735, 0.10, 0.985, 0.50)
    leg.SetHeader("#eta Range")
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetTextSize(0.026)
    for g in graphs:
        leg.AddEntry(g["graph"], g["eta"]["label"], "lp")
    leg.Draw()

    # Formula, sopra la legenda, sempre nel margine destro
    formula_box = ROOT.TPaveText(0.735, 0.55, 0.985, 0.90, "NDC")
    formula_box.SetBorderSize(1)
    formula_box.SetFillColor(ROOT.kWhite)
    formula_box.SetTextSize(0.030)
    formula_box.SetTextAlign(22)
    formula_box.AddText("#frac{#sigma_{p_{T}}}{p_{T}} =")
    formula_box.AddText("#sqrt{#frac{r_{0}^{2}}{p_{T}^{2}} + r_{1}^{2} + (r_{2} #times p_{T})^{2}}")
    formula_box.Draw()

    path = os.path.join(IMAGES_DIR, filename)
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")

    print(f"\n[INFO] Salvato: {path}.png / .pdf")
    print("\n=== Parametri del fit per bin di eta ===")
    for g in graphs:
        f = g["fit"]
        print(
            f"  {g['eta']['label']}: "
            f"r0={f.GetParameter(0):.3f}+-{f.GetParError(0):.3f}  "
            f"r1={f.GetParameter(1):.4f}+-{f.GetParError(1):.4f}  "
            f"r2={f.GetParameter(2):.6f}+-{f.GetParError(2):.6f}  "
            f"chi2/ndf={f.GetChisquare():.2f}/{f.GetNDF()}"
        )

    return c
