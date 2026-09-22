"""
Per ciascun bin di |eta| (stessi 6 di RMS_<eta>.pdf), sovrappone in un
unico canvas gli istogrammi del residuo (la variabile di risoluzione,
res = pT_true/pT_reco - 1, riempita in event_loop.py) per i bin di pT
dagli 800 GeV in su: 800-1200, 1200-1750 GeV -- gli ultimi punti "in
alto" di ciascun RMS_<eta>.pdf (il range adesso si ferma a 1750 GeV,
tolti i due bin oltre).

Ogni istogramma e' normalizzato ad area 1 (come draw_eta_overlay in
plotting.py) perche' le statistiche calano di ordini di grandezza
salendo in pT: senza normalizzare, i bin piu' bassi coprirebbero
visivamente gli altri.

Legge da merged_ZZallRMS.root (il merge dei 73 job Z+Z' aligned).
Output: ZZallRMS/residual_highpt_eta_<min>_<max>.png/.pdf

Uso: python3 plot_residual_overlay_highpt.py
"""

import ROOT

from config import ETA_BINS
from style import PALETTE, style_histo, make_legend
import style

style.apply_style()

MERGED = "merged_ZZallRMS.root"
IMAGES_DIR = "ZZallRMS"
HIGH_PT_BINS = [
    {"name": "800_1200", "min": 800, "max": 1200},
    {"name": "1200_1750", "min": 1200, "max": 1750},
]


def draw_for_eta(f, eta):
    kept = []
    y_max = 0.0

    for i, p in enumerate(HIGH_PT_BINS):
        name = f"h_res_{p['name']}_eta_{eta['min']}_{eta['max']}"
        h = f.Get(name)
        if not h:
            raise RuntimeError(f"Istogramma '{name}' non trovato in {MERGED}")
        h = h.Clone(f"{name}_clone")
        h.SetDirectory(0)

        entries = int(h.GetEntries())
        if entries == 0:
            print(f"  pT {p['min']}-{p['max']} GeV: 0 muoni, saltato")
            continue

        style_histo(h, PALETTE[i % len(PALETTE)])
        h.SetFillStyle(0)
        h.Scale(1.0 / h.Integral())
        y_max = max(y_max, h.GetMaximum())
        kept.append((p, h, entries))

    if not kept:
        print(f"  eta [{eta['min']}, {eta['max']}): nessun bin con statistica, salto il plot")
        return None

    c = ROOT.TCanvas(f"c_residual_highpt_eta_{eta['min']}_{eta['max']}",
                      "Residuo, bin di pT >= 800 GeV", 950, 700)
    leg = make_legend(0.63, 0.55, 0.92, 0.90)
    leg.SetHeader(f"|#eta^{{truth}}| #in [{eta['min']:.2f}, {eta['max']:.2f})", "C")

    for j, (p, h, entries) in enumerate(kept):
        h.SetMaximum(y_max * 1.35)
        h.GetXaxis().SetTitle("(p_{T}^{truth}/p_{T}^{reco}) - 1")
        h.GetYaxis().SetTitle("Fraction of muons / bin")
        h.Draw("HIST" if j == 0 else "HIST SAME")
        leg.AddEntry(h, f"p_{{T}} #in [{p['min']}, {p['max']}) GeV", "l")
        print(f"  pT {p['min']}-{p['max']} GeV: {entries} muoni")

    leg.Draw()

    path = f"{IMAGES_DIR}/residual_highpt_eta_{eta['min']}_{eta['max']}"
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"  Plot salvato in {path}.png (.pdf)")
    return c, kept, leg


def main():
    f = ROOT.TFile.Open(MERGED)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {MERGED}")

    # Solo la regione [0.1, 1.01) -- richiesta esplicita, non tutti i
    # 6 bin di eta.
    target = next(e for e in ETA_BINS if e["min"] == 0.1 and e["max"] == 1.01)

    survivors = []
    print(f"\n=== eta bin [{target['min']}, {target['max']}) ===")
    result = draw_for_eta(f, target)
    if result:
        survivors.append(result)

    f.Close()
    print(f"\n[INFO] Fatto: {len(survivors)}/{len(ETA_BINS)} plot generati in {IMAGES_DIR}/")


if __name__ == "__main__":
    main()
