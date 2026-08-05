"""
Genera in PDF/PNG i due output diagnostici di bin_stats.py:
1. un istogramma a barre (scala log, categoriche/staccate) degli eventi
   totali per bin di pT (sommati su tutti i bin di eta)
2. una tabella con gli entries per ogni combinazione (bin pT, bin eta)

Disegnati con ROOT (TBox/TLatex), nessuna libreria esterna -- gira
nello stesso ambiente (LCG + ROOT) usato per il resto dell'analisi.
Testo in inglese, nessun riferimento al progetto/tesi.

NOTA SU UN BUG RISOLTO: gli oggetti TBox/TLine creati "a mano" dentro
un ciclo (uno per riga/colonna della tabella, uno per barra
dell'istogramma) possono essere eliminati dal garbage collector di
Python prima che il canvas venga salvato su disco, se non si tiene un
riferimento persistente -- il sintomo tipico e' un elemento (es. una
colonna intera) che sparisce dal PDF pur essendo stato disegnato nel
codice. Per questo ogni funzione qui sotto accumula tutti gli oggetti
creati in una lista locale (_keep) che resta viva fino al termine
della funzione (dopo il salvataggio del canvas).
"""

import os
import ROOT

IMAGES_DIR = "images"

_HEADER_HEX = "#16213e"
_ZEBRA_HEX = "#f0f0f5"
_LOW_STAT_HEX = "#8b1e1e"
_header_color = ROOT.TColor.GetColor(_HEADER_HEX)
_zebra_color = ROOT.TColor.GetColor(_ZEBRA_HEX)
_low_stat_color = ROOT.TColor.GetColor(_LOW_STAT_HEX)


def plot_event_distribution(counts, pt_edges, filename="event_distribution_vs_pt"):
    """Istogramma a barre (log-y) degli eventi totali per bin di pT,
    sommati su tutti i bin di eta, con un box "Summary Details" sotto.

    Le barre sono disegnate MANUALMENTE come TBox (non con l'opzione
    "BAR" di TH1), cosi' il bordo (SetLineColor/Width) e' garantito
    visibile -- l'opzione "BAR" di ROOT non sempre applica in modo
    affidabile lo spessore della linea di contorno.
    """
    os.makedirs(IMAGES_DIR, exist_ok=True)
    _keep = []  # tiene in vita tutti gli oggetti fino al salvataggio del canvas

    n_pt = len(pt_edges) - 1
    n_eta = len(counts)
    totals_per_pt = [sum(counts[e_i][p_i] for e_i in range(n_eta)) for p_i in range(n_pt)]
    grand_total = sum(totals_per_pt)

    # Istogramma "invisibile", usato solo per impostare correttamente
    # frame, assi, range e griglia in scala log -- le barre vere sono
    # disegnate a parte come TBox.
    h = ROOT.TH1F("h_event_dist", "", n_pt, 0.5, n_pt + 0.5)
    for p_i, n in enumerate(totals_per_pt):
        h.SetBinContent(p_i + 1, max(n, 0))
    h.SetFillStyle(0)
    h.SetLineWidth(0)

    c = ROOT.TCanvas("c_event_dist", "Event distribution vs pT", 1200, 900)

    pad_plot = ROOT.TPad("pad_plot", "", 0.0, 0.20, 1.0, 1.0)
    pad_summary = ROOT.TPad("pad_summary", "", 0.0, 0.0, 1.0, 0.20)
    pad_plot.SetBottomMargin(0.22)
    pad_plot.SetTopMargin(0.10)
    pad_plot.SetLeftMargin(0.09)
    pad_plot.SetRightMargin(0.03)
    pad_plot.SetLogy()
    pad_plot.SetGrid(0, 1)
    pad_summary.SetMargin(0, 0, 0, 0)
    pad_plot.Draw()
    pad_summary.Draw()
    _keep += [pad_plot, pad_summary]

    # ---------------- Pad del grafico ----------------
    pad_plot.cd()

    h.GetYaxis().SetTitle("Total Event Count (Log Scale)")
    h.GetYaxis().SetTitleSize(0.032)
    h.GetXaxis().SetLabelSize(0)
    h.GetXaxis().SetTickLength(0.015)
    h.SetMaximum(max(totals_per_pt) * 6)
    h.SetMinimum(1)
    h.Draw("AXIS")  # solo il frame/assi, niente barre da qui
    h.GetXaxis().SetRangeUser(0.0, n_pt + 1.0)
    _keep.append(h)

    # Barre disegnate a mano: bordo blu scuro garantito, riempimento
    # blu chiaro leggermente sfumato
    bar_half_width = 0.40  # 0.80 di larghezza totale, come prima (gap tra le barre)
    for p_i, n in enumerate(totals_per_pt):
        if n <= 0:
            continue
        x_center = p_i + 1
        bar = ROOT.TBox(x_center - bar_half_width, 1, x_center + bar_half_width, n)
        bar.SetFillColorAlpha(ROOT.TColor.GetColor("#7fa0d4"), 0.80)
        bar.SetLineColor(_header_color)
        bar.SetLineWidth(2)
        bar.Draw()
        _keep.append(bar)

    title = ROOT.TLatex()
    title.SetNDC()
    title.SetTextFont(62)
    title.SetTextSize(0.038)
    title.SetTextAlign(21)
    title.DrawLatex(0.53, 0.94, "Event Distribution vs p_{T} (Log Scale Y-Axis)")

    bin_lat = ROOT.TLatex()
    bin_lat.SetTextFont(42)
    bin_lat.SetTextSize(0.017)
    bin_lat.SetTextAlign(31)
    bin_lat.SetTextAngle(35)

    y_axis_min = h.GetMinimum()
    for p_i in range(n_pt):
        lo, hi = pt_edges[p_i], pt_edges[p_i + 1]
        label = f"{lo:.0f}-{hi:.0f}"
        bin_lat.DrawLatex(p_i + 1, y_axis_min * 0.55, label)

    xtitle = ROOT.TLatex()
    xtitle.SetNDC()
    xtitle.SetTextFont(42)
    xtitle.SetTextSize(0.028)
    xtitle.SetTextAlign(21)
    xtitle.DrawLatex(0.53, 0.05, "p_{T} Range [GeV]")

    val_lat = ROOT.TLatex()
    val_lat.SetTextFont(42)
    val_lat.SetTextSize(0.015)
    val_lat.SetTextAlign(21)
    val_lat.SetTextAngle(90)
    for p_i, n in enumerate(totals_per_pt):
        if n <= 0:
            continue
        val_lat.DrawLatex(p_i + 1, n * 1.3, f"{n:,}")

    # ---------------- Pad del box riepilogativo ----------------
    pad_summary.cd()

    box_bg = ROOT.TBox(0.02, 0.06, 0.98, 0.94)
    box_bg.SetFillColor(ROOT.TColor.GetColor("#eef3fb"))
    box_bg.SetLineColor(ROOT.TColor.GetColor("#c7d4ea"))
    box_bg.SetLineWidth(1)
    box_bg.Draw()
    _keep.append(box_bg)

    accent = ROOT.TBox(0.02, 0.06, 0.028, 0.94)
    accent.SetFillColor(_header_color)
    accent.SetLineWidth(0)
    accent.Draw()
    _keep.append(accent)

    heading = ROOT.TLatex()
    heading.SetTextFont(62)
    heading.SetTextSize(0.16)
    heading.SetTextAlign(12)
    heading.DrawLatex(0.05, 0.80, "Summary Details:")

    lines = [
        ("Total Events Analyzed: ", f"{grand_total:,}"),
        ("Kinematic Bins: ", f"{n_pt} p_{{T}} bins spanning from {pt_edges[0]:.0f} GeV to {pt_edges[-1]:.0f} GeV"),
        ("Y-Axis: ", "Logarithmic scale (Base 10) for high-dynamic-range visualization across high p_{T} regimes"),
    ]
    label_lat = ROOT.TLatex()
    label_lat.SetTextFont(62)
    label_lat.SetTextSize(0.12)
    label_lat.SetTextAlign(12)

    value_lat = ROOT.TLatex()
    value_lat.SetTextFont(42)
    value_lat.SetTextSize(0.12)
    value_lat.SetTextAlign(12)

    y_positions = [0.56, 0.36, 0.16]
    for (label, value), y_pos in zip(lines, y_positions):
        label_lat.DrawLatex(0.05, y_pos, f"#bullet {label}")
        x_value = 0.05 + 0.014 * len(label) + 0.015
        value_lat.DrawLatex(x_value, y_pos, value)

    path = os.path.join(IMAGES_DIR, filename)
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"[INFO] Saved {path}.png / .pdf")

    return grand_total, totals_per_pt


def build_stats_table_pdf(counts, pt_edges, eta_bins, min_entries_for_fit,
                           filename="table_stats_per_pt_bin.pdf"):
    """Tabella con gli entries per ogni combinazione (bin pT, bin eta).

    Schema colori:
    - colonna del bin di pT (prima colonna) e riga dei Totali: blu scuro
      pieno (come l'header), testo bianco
    - corpo della tabella: TUTTE le righe colorate, alternando due
      tonalita' di blu chiaro (nessuna riga bianca)
    - celle sotto soglia: overlay rosso, oltre all'asterisco
    """
    os.makedirs(IMAGES_DIR, exist_ok=True)
    output_path = os.path.join(IMAGES_DIR, filename)
    _keep = []  # tiene in vita tutti gli oggetti fino al salvataggio del canvas

    n_pt = len(pt_edges) - 1
    n_eta = len(eta_bins)

    eta_totals = [sum(counts[e_i][p_i] for p_i in range(n_pt)) for e_i in range(n_eta)]
    pt_totals = [sum(counts[e_i][p_i] for e_i in range(n_eta)) for p_i in range(n_pt)]
    grand_total = sum(eta_totals)
    n_low_stat = sum(
        1 for e_i in range(n_eta) for p_i in range(n_pt)
        if counts[e_i][p_i] < min_entries_for_fit
    )

    _row_light = ROOT.TColor.GetColor("#eef3fb")
    _row_medium = ROOT.TColor.GetColor("#c9d9f0")
    _low_stat_overlay_alpha = 0.30

    c = ROOT.TCanvas("c_stats_table", "Entries per pT x eta bin", 1150, 1400)
    for setter in (c.SetLeftMargin, c.SetRightMargin, c.SetTopMargin, c.SetBottomMargin):
        setter(0.0)
    c.Range(0, 0, 1, 1)

    x0, x1 = 0.03, 0.97
    n_cols = n_eta + 2
    col_w = (x1 - x0) / n_cols
    col_edges = [x0 + i * col_w for i in range(n_cols + 1)]

    title = ROOT.TLatex()
    title.SetTextFont(62)
    title.SetTextSize(0.026)
    title.SetTextAlign(22)
    title.DrawLatex(0.5, 0.975, "Entries per p_{T} x #eta bin")

    subtitle = ROOT.TLatex()
    subtitle.SetTextFont(42)
    subtitle.SetTextSize(0.015)
    subtitle.SetTextColor(ROOT.kGray + 2)
    subtitle.SetTextAlign(22)
    subtitle.DrawLatex(0.5, 0.958,
                        f"Red: below the minimum for a stable fit (MIN_ENTRIES_FOR_FIT = {min_entries_for_fit})")

    top = 0.93
    bottom = 0.08
    header_h = 0.022
    total_row_h = 0.022
    n_rows = n_pt
    row_h = (top - header_h - total_row_h - bottom) / n_rows

    # ---------------- Header ----------------
    header_box = ROOT.TBox(x0, top - header_h, x1, top)
    header_box.SetFillColor(_header_color)
    header_box.Draw()
    _keep.append(header_box)

    header_lat = ROOT.TLatex()
    header_lat.SetTextFont(62)
    header_lat.SetTextSize(0.013)
    header_lat.SetTextColor(ROOT.kWhite)
    header_lat.SetTextAlign(22)
    y_mid = top - header_h / 2.0
    header_lat.DrawLatex((col_edges[0] + col_edges[1]) / 2.0, y_mid, "p_{T} [GeV]")
    for e_i in range(n_eta):
        header_lat.DrawLatex((col_edges[1 + e_i] + col_edges[2 + e_i]) / 2.0, y_mid, f"#eta bin {e_i}")
    header_lat.DrawLatex((col_edges[-2] + col_edges[-1]) / 2.0, y_mid, "Total")

    # ---------------- Corpo della tabella ----------------
    y = top - header_h

    stub_lat = ROOT.TLatex()
    stub_lat.SetTextFont(62)
    stub_lat.SetTextSize(0.0115)
    stub_lat.SetTextColor(ROOT.kWhite)
    stub_lat.SetTextAlign(22)

    body_lat = ROOT.TLatex()
    body_lat.SetTextFont(42)
    body_lat.SetTextSize(0.0115)
    body_lat.SetTextAlign(22)

    for p_i in range(n_pt):
        row_color = _row_light if p_i % 2 == 0 else _row_medium

        row_box = ROOT.TBox(x0, y - row_h, x1, y)
        row_box.SetFillColor(row_color)
        row_box.SetLineWidth(0)
        row_box.Draw()
        _keep.append(row_box)

        y_mid = y - row_h / 2.0

        stub_box = ROOT.TBox(col_edges[0], y - row_h, col_edges[1], y)
        stub_box.SetFillColor(_header_color)
        stub_box.SetLineWidth(0)
        stub_box.Draw()
        _keep.append(stub_box)

        lo, hi = pt_edges[p_i], pt_edges[p_i + 1]
        stub_lat.DrawLatex((col_edges[0] + col_edges[1]) / 2.0, y_mid, f"{lo:.0f}-{hi:.0f}")

        for e_i in range(n_eta):
            n = counts[e_i][p_i]
            is_low = n < min_entries_for_fit

            if is_low:
                cell_box = ROOT.TBox(col_edges[1 + e_i], y - row_h, col_edges[2 + e_i], y)
                cell_box.SetFillColorAlpha(_low_stat_color, _low_stat_overlay_alpha)
                cell_box.SetLineWidth(0)
                cell_box.Draw()
                _keep.append(cell_box)

            txt = f"{n:,}" + ("*" if is_low else "")
            body_lat.DrawLatex((col_edges[1 + e_i] + col_edges[2 + e_i]) / 2.0, y_mid, txt)

        body_lat.DrawLatex((col_edges[-2] + col_edges[-1]) / 2.0, y_mid, f"{pt_totals[p_i]:,}")

        y -= row_h

    # ---------------- Riga dei totali ----------------
    total_box = ROOT.TBox(x0, y - total_row_h, x1, y)
    total_box.SetFillColor(_header_color)
    total_box.Draw()
    _keep.append(total_box)

    total_lat = ROOT.TLatex()
    total_lat.SetTextFont(62)
    total_lat.SetTextSize(0.013)
    total_lat.SetTextColor(ROOT.kWhite)
    total_lat.SetTextAlign(22)
    y_mid = y - total_row_h / 2.0
    total_lat.DrawLatex((col_edges[0] + col_edges[1]) / 2.0, y_mid, "Total")
    for e_i in range(n_eta):
        total_lat.DrawLatex((col_edges[1 + e_i] + col_edges[2 + e_i]) / 2.0, y_mid, f"{eta_totals[e_i]:,}")
    total_lat.DrawLatex((col_edges[-2] + col_edges[-1]) / 2.0, y_mid, f"{grand_total:,}")
    y -= total_row_h

    table_bottom = y
    for xe in col_edges[1:-1]:
        vline = ROOT.TLine(xe, table_bottom, xe, top)
        vline.SetLineColor(ROOT.kWhite)
        vline.SetLineWidth(1)
        vline.Draw()
        _keep.append(vline)

    border = ROOT.TBox(x0, table_bottom, x1, top)
    border.SetFillStyle(0)
    border.SetLineColor(_header_color)
    border.SetLineWidth(2)
    border.Draw()
    _keep.append(border)

    footer = ROOT.TLatex()
    footer.SetTextFont(42)
    footer.SetTextSize(0.013)
    footer.SetTextColor(ROOT.kGray + 2)
    footer.SetTextAlign(22)
    footer.DrawLatex(0.5, table_bottom - 0.03,
                      f"Total events: {grand_total:,}  --  Kinematic bins: {n_pt} p_{{T}} x {n_eta} #eta = {n_pt*n_eta}  --  Bins below threshold: {n_low_stat}")

    c.SaveAs(output_path)
    print(f"[INFO] Saved {output_path}")
    return c