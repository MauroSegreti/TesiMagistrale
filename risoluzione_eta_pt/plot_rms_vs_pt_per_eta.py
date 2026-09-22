"""
RMS della risoluzione in p_T in funzione di p_T, un plot per ciascun bin
di |eta^{truth}| -- un punto per ogni bin di p_T, ciascuno con un
colore diverso.

x     = centro del bin di p_T
ex    = meta' larghezza del bin di p_T
y     = RMS dell'istogramma di risoluzione in quel bin (pT, eta)
ey    = errore sulla RMS (TH1::GetRMSError())

Legenda fuori dall'area dati: intestazione con il bin di eta, una voce
su due righe per punto (range di p_T + RMS corrispondente), e in fondo
la formula dell'errore sull'asse x.

Un file per bin di eta: images/RMS_<eta_min>_<eta_max>.pdf (+ .png)

Uso: python3 plot_rms_vs_pt_per_eta.py [merged_eta.root]
"""

import os
import sys
import array
import ROOT

from config import PT_BINS, ETA_BINS
from style import PALETTE
import style

style.apply_style()

IMAGES_DIR = "images"


def fmt6(x):
    """Arrotonda x a 6 cifre decimali (notazione fissa)."""
    return f"{x:.6f}"


def load_points(f, eta):
    points = []
    for p in PT_BINS:
        name = f"h_res_{p['name']}_eta_{eta['min']}_{eta['max']}"
        h = f.Get(name)
        if not h:
            raise RuntimeError(f"Istogramma '{name}' non trovato")

        pt_center = (p["min"] + p["max"]) / 2.0
        pt_half_width = (p["max"] - p["min"]) / 2.0
        rms = h.GetRMS()
        rms_err = h.GetRMSError()

        points.append({
            "pt_min": p["min"], "pt_max": p["max"],
            "x": pt_center, "ex": pt_half_width,
            "y": rms, "ey": rms_err,
        })

    return points


def draw(points, eta):
    os.makedirs(IMAGES_DIR, exist_ok=True)

    print(f"\n=== eta bin [{eta['min']}, {eta['max']}) ===")
    for pt in points:
        print(f"  pT {pt['pt_min']}-{pt['pt_max']} GeV (centro={pt['x']:.1f}, "
              f"errore={pt['ex']:.1f}): RMS={pt['y']:.4f} +- {pt['ey']:.5f}")

    cname = f"c_rms_vs_pt_eta_{eta['min']}_{eta['max']}"
    c = ROOT.TCanvas(cname, cname, 1200, 750)
    # Margine destro allargato per ospitare la legenda fuori dall'area dati
    c.SetRightMargin(0.38)

    graphs = []
    for i, pt in enumerate(points):
        x = array.array('d', [pt["x"]])
        y = array.array('d', [pt["y"]])
        ex = array.array('d', [pt["ex"]])
        ey = array.array('d', [pt["ey"]])
        g = ROOT.TGraphErrors(1, x, y, ex, ey)
        color = PALETTE[i % len(PALETTE)]
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.SetMarkerStyle(20)
        g.SetMarkerSize(1.4)
        g.SetLineWidth(2)
        g.SetTitle("")
        graphs.append(g)

    all_y = [pt["y"] for pt in points]
    ymin, ymax = min(all_y) * 0.8, max(all_y) * 1.15
    all_x = [pt["x"] for pt in points]
    all_ex = [pt["ex"] for pt in points]
    xmin = min(x - ex for x, ex in zip(all_x, all_ex))
    xmax = max(x + ex for x, ex in zip(all_x, all_ex))

    frame = c.DrawFrame(xmin - 0.05 * (xmax - xmin), ymin,
                         xmax + 0.05 * (xmax - xmin), ymax)
    frame.GetXaxis().SetTitle("p_{T}^{truth} [GeV]")
    frame.GetYaxis().SetTitle("p_{T} resolution RMS")

    for g in graphs:
        g.Draw("P SAME")

    # --- Legenda fuori dall'area dati, nel margine destro ---
    # Riquadro e dimensione del testo scalati sul numero di bin di pT: con
    # solo 6 bin (Z) il riquadro 0.16-0.88 bastava, ma con piu' bin (es. i
    # 14 fino a 3 TeV di Z+Z') le voci (due righe ciascuna, via
    # #splitline) iniziano a sovrapporsi se non si allarga il riquadro e
    # non si rimpicciolisce il testo di conseguenza.
    n_entries = len(points) + 1  # +1 per la riga della formula sigma_pT
    leg_y0, leg_y1 = 0.04, 0.94
    leg = ROOT.TLegend(0.65, leg_y0, 0.985, leg_y1)
    leg.SetBorderSize(1)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetTextFont(42)
    leg.SetTextSize(min(0.022, 0.30 * (leg_y1 - leg_y0) / n_entries))
    leg.SetHeader(f"|#eta^{{truth}}| #in [{eta['min']:.2f}, {eta['max']:.2f})", "C")

    for pt, g in zip(points, graphs):
        leg.AddEntry(g, f"#splitline{{p_{{T}} #in [{pt['pt_min']}, {pt['pt_max']}) GeV:}}"
                         f"{{RMS = {fmt6(pt['y'])} #pm {fmt6(pt['ey'])}}}", "p")

    # Formula dell'errore sull'asse x, come ultima riga della legenda stessa
    leg.AddEntry(0, "#sigma_{p_{T}} = #frac{p_{T}^{max} - p_{T}^{min}}{2}", "")

    leg.Draw()

    path = os.path.join(IMAGES_DIR, f"RMS_{eta['min']}_{eta['max']}")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"[INFO] Plot salvato in {path}.png (.pdf)")
    return c, graphs, leg


if __name__ == "__main__":
    merged = sys.argv[1] if len(sys.argv) > 1 else "merged_eta.root"
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    kept = []
    for eta in ETA_BINS:
        points = load_points(f, eta)
        c, graphs, leg = draw(points, eta)
        kept.append((c, graphs, leg))

    f.Close()
