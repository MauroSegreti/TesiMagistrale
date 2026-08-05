"""
Genera una tabella PDF con i parametri del fit per ogni bin di eta,
confrontando r0 libero vs r0 fissato a 0 (richiesta di Luca), e
mettendo in evidenza r2 -- il risultato che interessa di piu'
("quello che ci interessa e' vedere quanto viene r2, che sara' la
risoluzione NOMINALE che abbiamo in ATLAS ad alto pT").
"""

import os
import ROOT

IMAGES_DIR = "images"

_HEADER_HEX = "#16213e"
_ZEBRA_HEX = "#f0f0f5"
_BAD_FIT_HEX = "#8b1e1e"
_R2_HEX = "#0f3460"
_header_color = ROOT.TColor.GetColor(_HEADER_HEX)
_zebra_color = ROOT.TColor.GetColor(_ZEBRA_HEX)
_bad_fit_color = ROOT.TColor.GetColor(_BAD_FIT_HEX)
_r2_color = ROOT.TColor.GetColor(_R2_HEX)

_COL_EDGES = [0.03, 0.24, 0.37, 0.50, 0.66, 0.80, 0.97]
_COL_LABELS = ["|#eta| bin", "n pt", "r_{0} free", "#chi^{2}/ndf free", "#chi^{2}/ndf fix r_{0}=0", "r_{2} [GeV^{-1}]"]

_CHI2_NDF_WARN = 3.0


def build_table_pdf(graphs, filename="table_res_vs_pt.pdf"):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    output_path = os.path.join(IMAGES_DIR, filename)

    c = ROOT.TCanvas("c_table_fit", "Tabella parametri fit", 1000, 500)
    for setter in (c.SetLeftMargin, c.SetRightMargin, c.SetTopMargin, c.SetBottomMargin):
        setter(0.0)
    c.Range(0, 0, 1, 1)

    x0, x1 = _COL_EDGES[0], _COL_EDGES[-1]

    title = ROOT.TLatex()
    title.SetTextFont(62)
    title.SetTextSize(0.042)
    title.SetTextAlign(22)
    title.DrawLatex(0.5, 0.94, "Fit risoluzione in p_{T} vs |#eta^{truth}|: r_{0} libero vs r_{0} = 0")

    subtitle = ROOT.TLatex()
    subtitle.SetTextFont(42)
    subtitle.SetTextSize(0.024)
    subtitle.SetTextColor(ROOT.kGray + 2)
    subtitle.SetTextAlign(22)
    subtitle.DrawLatex(0.5, 0.885,
                        "#sigma_{p_{T}}/p_{T} = #sqrt{r_{0}^{2}/p_{T}^{2} + r_{1}^{2} + (r_{2} #times p_{T})^{2}}  --  tutti i sample combinati (Z + Z')")

    n_rows = len(graphs)
    top = 0.79
    bottom = 0.10
    header_h = 0.09
    row_h = (top - header_h - bottom) / n_rows

    header_box = ROOT.TBox(x0, top - header_h, x1, top)
    header_box.SetFillColor(_header_color)
    header_box.Draw()

    header_lat = ROOT.TLatex()
    header_lat.SetTextFont(62)
    header_lat.SetTextSize(0.024)
    header_lat.SetTextColor(ROOT.kWhite)
    header_lat.SetTextAlign(12)
    y_mid = top - header_h / 2.0
    for xe, label in zip(_COL_EDGES[:-1], _COL_LABELS):
        header_lat.DrawLatex(xe + 0.008, y_mid, label)

    y = top - header_h
    body_lat = ROOT.TLatex()
    body_lat.SetTextFont(42)
    body_lat.SetTextSize(0.022)
    body_lat.SetTextAlign(12)

    warn_lat = ROOT.TLatex()
    warn_lat.SetTextFont(62)
    warn_lat.SetTextSize(0.022)
    warn_lat.SetTextColor(_bad_fit_color)
    warn_lat.SetTextAlign(12)

    r2_lat = ROOT.TLatex()
    r2_lat.SetTextFont(62)
    r2_lat.SetTextSize(0.024)
    r2_lat.SetTextColor(_r2_color)
    r2_lat.SetTextAlign(12)

    for i, g in enumerate(graphs):
        f_free = g["fit"]
        f_fix0 = g["fit_fixed0"]
        chi2ndf_free = f_free.GetChisquare() / f_free.GetNDF() if f_free.GetNDF() > 0 else float("nan")
        chi2ndf_fix0 = f_fix0.GetChisquare() / f_fix0.GetNDF() if f_fix0.GetNDF() > 0 else float("nan")

        if i % 2 == 1:
            zebra = ROOT.TBox(x0, y - row_h, x1, y)
            zebra.SetFillColor(_zebra_color)
            zebra.SetLineWidth(0)
            zebra.Draw()

        y_mid = y - row_h / 2.0

        body_lat.DrawLatex(_COL_EDGES[0] + 0.008, y_mid, g["eta"]["label"])
        body_lat.DrawLatex(_COL_EDGES[1] + 0.008, y_mid, f"{g['n_points']}")
        body_lat.DrawLatex(_COL_EDGES[2] + 0.008, y_mid,
                            f"{f_free.GetParameter(0):.3f} #pm {f_free.GetParError(0):.3f}")

        lat_free = warn_lat if chi2ndf_free > _CHI2_NDF_WARN else body_lat
        lat_free.DrawLatex(_COL_EDGES[3] + 0.008, y_mid, f"{chi2ndf_free:.2f}")

        lat_fix0 = warn_lat if chi2ndf_fix0 > _CHI2_NDF_WARN else body_lat
        lat_fix0.DrawLatex(_COL_EDGES[4] + 0.008, y_mid, f"{chi2ndf_fix0:.2f}")

        # r2 evidenziato: e' il risultato che interessa di piu'
        r2_lat.DrawLatex(_COL_EDGES[5] + 0.008, y_mid,
                          f"{f_free.GetParameter(2)*1000:.3f} #pm {f_free.GetParError(2)*1000:.3f}  (#times10^{{-3}})")

        y -= row_h

    table_bottom = y
    for xe in _COL_EDGES[1:-1]:
        vline = ROOT.TLine(xe, table_bottom, xe, top)
        vline.SetLineColor(ROOT.kGray + 1)
        vline.Draw()

    border = ROOT.TBox(x0, table_bottom, x1, top)
    border.SetFillStyle(0)
    border.SetLineColor(_header_color)
    border.SetLineWidth(2)
    border.Draw()

    footer1 = ROOT.TLatex()
    footer1.SetTextFont(42)
    footer1.SetTextSize(0.018)
    footer1.SetTextColor(_bad_fit_color)
    footer1.SetTextAlign(22)
    footer1.DrawLatex(0.5, table_bottom - 0.045,
                       "In rosso: #chi^{2}/ndf > 3, fit poco affidabile")

    footer2 = ROOT.TLatex()
    footer2.SetTextFont(42)
    footer2.SetTextSize(0.018)
    footer2.SetTextColor(_r2_color)
    footer2.SetTextAlign(22)
    footer2.DrawLatex(0.5, table_bottom - 0.075,
                       "In blu: r_{2}, la risoluzione nominale ATLAS ad alto p_{T}")

    c.SaveAs(output_path)
    print(f"[INFO] Tabella salvata in {output_path}")
    return c
