"""
Genera una tabella PDF professionale con tutti i valori (entries, RMS,
RMS error) per ogni combinazione di bin pT x eta -- la stessa
informazione stampata a console durante build_rms_graphs, ma
presentata con un layout leggibile: intestazioni di gruppo per bin di
pT, righe alternate (zebra), bordo esterno.

Disegnata interamente con ROOT (TBox/TLine/TLatex), così non serve
installare nessuna libreria PDF esterna: gira con lo stesso ambiente
(LCG + ROOT) già usato per il resto dell'analisi.
"""

import os
import ROOT

IMAGES_DIR = "images"

# Palette "corporate" per l'intestazione
_HEADER_HEX = "#16213e"    # blu molto scuro: barra colonne
_GROUP_HEX = "#0f3460"     # blu scuro: barra di ogni bin di pT
_ZEBRA_HEX = "#f0f0f5"     # grigio chiaro: righe alternate
_BORDER_HEX = "#16213e"

_header_color = ROOT.TColor.GetColor(_HEADER_HEX)
_group_color = ROOT.TColor.GetColor(_GROUP_HEX)
_zebra_color = ROOT.TColor.GetColor(_ZEBRA_HEX)
_border_color = ROOT.TColor.GetColor(_BORDER_HEX)

# Bordi orizzontali delle 4 colonne (in coordinate NDC 0-1)
_COL_EDGES = [0.05, 0.42, 0.62, 0.80, 0.95]
_COL_LABELS = ["|#eta^{truth}| bin", "Entries", "RMS", "RMS error"]


def _group_rows(results):
    """Raggruppa i risultati per bin di pT, mantenendo l'ordine originale."""
    groups = []
    for r in results:
        if not groups or groups[-1]["pt_name"] != r["pt_name"]:
            groups.append({"pt_name": r["pt_name"], "pt_min": r["pt_min"],
                            "pt_max": r["pt_max"], "rows": []})
        groups[-1]["rows"].append(r)
    return groups


def build_table_pdf(results, filename="table_RMS_vs_eta.pdf"):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    output_path = os.path.join(IMAGES_DIR, filename)

    groups = _group_rows(results)
    n_groups = len(groups)
    n_rows = len(results)

    c = ROOT.TCanvas("c_table", "Tabella risultati", 850, 1150)
    for setter in (c.SetLeftMargin, c.SetRightMargin, c.SetTopMargin, c.SetBottomMargin):
        setter(0.0)
    c.Range(0, 0, 1, 1)

    x0, x1 = _COL_EDGES[0], _COL_EDGES[-1]

    # --- Titolo ---
    title = ROOT.TLatex()
    title.SetTextFont(62)
    title.SetTextSize(0.024)
    title.SetTextAlign(22)
    title.DrawLatex(0.5, 0.965, "RMS della risoluzione in p_{T}")

    subtitle = ROOT.TLatex()
    subtitle.SetTextFont(42)
    subtitle.SetTextSize(0.014)
    subtitle.SetTextColor(ROOT.kGray + 2)
    subtitle.SetTextAlign(22)
    subtitle.DrawLatex(0.5, 0.945, "per bin di p_{T} e |#eta^{truth}| -- soli muoni truth prompt (IFFType == 4)")

    # --- Geometria righe (con scala automatica se non ci stanno) ---
    row_h = 0.017
    group_h = 0.026
    top = 0.905
    bottom = 0.05
    total_h = n_groups * group_h + n_rows * row_h
    available = top - bottom
    scale = min(1.0, available / total_h) if total_h > 0 else 1.0
    row_h *= scale
    group_h *= scale

    table_top = top

    # --- Intestazione colonne (una volta sola, sopra il primo gruppo) ---
    header_h = group_h * 0.85
    header_box = ROOT.TBox(x0, top - header_h, x1, top)
    header_box.SetFillColor(_header_color)
    header_box.Draw()

    header_lat = ROOT.TLatex()
    header_lat.SetTextFont(62)
    header_lat.SetTextSize(0.014)
    header_lat.SetTextColor(ROOT.kWhite)
    header_lat.SetTextAlign(12)
    y_mid = top - header_h / 2.0
    for xe, label in zip(_COL_EDGES[:-1], _COL_LABELS):
        header_lat.DrawLatex(xe + 0.015, y_mid, label)

    y = top - header_h

    group_lat = ROOT.TLatex()
    group_lat.SetTextFont(62)
    group_lat.SetTextSize(0.015)
    group_lat.SetTextColor(ROOT.kWhite)
    group_lat.SetTextAlign(12)

    body_lat = ROOT.TLatex()
    body_lat.SetTextFont(42)
    body_lat.SetTextSize(0.0135)
    body_lat.SetTextAlign(12)

    for grp in groups:
        # --- Barra di gruppo: "pT = X-Y GeV", a tutta larghezza ---
        gbox = ROOT.TBox(x0, y - group_h, x1, y)
        gbox.SetFillColor(_group_color)
        gbox.Draw()
        y_mid = y - group_h / 2.0
        group_lat.DrawLatex(x0 + 0.015, y_mid, f"p_{{T}} = {grp['pt_min']} - {grp['pt_max']} GeV")
        y -= group_h

        for i, r in enumerate(grp["rows"]):
            if i % 2 == 1:
                zebra = ROOT.TBox(x0, y - row_h, x1, y)
                zebra.SetFillColor(_zebra_color)
                zebra.SetLineWidth(0)
                zebra.Draw()

            y_mid = y - row_h / 2.0
            values = [
                f"[{r['eta_min']:.2f}, {r['eta_max']:.2f})",
                f"{r['entries']}",
                f"{r['rms']:.4f}",
                f"{r['rms_err']:.6f}",
            ]
            for xe, v in zip(_COL_EDGES[:-1], values):
                body_lat.DrawLatex(xe + 0.015, y_mid, v)

            y -= row_h

    table_bottom = y

    # --- Linee verticali di separazione tra colonne ---
    for xe in _COL_EDGES[1:-1]:
        vline = ROOT.TLine(xe, table_bottom, xe, table_top)
        vline.SetLineColor(ROOT.kGray + 1)
        vline.Draw()

    # --- Bordo esterno ---
    border = ROOT.TBox(x0, table_bottom, x1, table_top)
    border.SetFillStyle(0)
    border.SetLineColor(_border_color)
    border.SetLineWidth(2)
    border.Draw()

    # --- Footer ---
    footer = ROOT.TLatex()
    footer.SetTextFont(42)
    footer.SetTextSize(0.011)
    footer.SetTextColor(ROOT.kGray + 2)
    footer.SetTextAlign(22)
    footer.DrawLatex(0.5, max(table_bottom - 0.025, 0.015),
                      "Generato automaticamente da main.py -- risoluzione_eta_pt")

    c.SaveAs(output_path)
    print(f"[INFO] Tabella salvata in {output_path}")
    return c
