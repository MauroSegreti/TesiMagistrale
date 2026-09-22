"""
Plot rapido: numero di muoni (Z aligned + Z' aligned combinati, stessa
statistica di ZZallRMS/) in funzione di |eta_truth|, selezionando solo
i muoni con p_T >= 1.2 TeV.

Riusa gli istogrammi gia' salvati in merged_ZZallRMS.root (il merge dei
73 job di combine/main_zzall.py): l'entries di ciascun istogramma
h_res_<bin_pt>_eta_<min>_<max> e' gia' il conteggio dei muoni in quella
cella pT x eta, quindi basta sommare le entries dei bin di pT sopra 1.2
TeV (1200-1750, 1750-2500, 2500-3000 -- il campione combinato non ha
statistica oltre i 3 TeV, quindi la selezione e' di fatto "1.2 TeV <= pT
< 3 TeV").

Uso: python3 plot_muon_count_highpt.py
"""

import array
import ROOT

from config import ETA_BINS
import style

style.apply_style()

MERGED = "merged_ZZallRMS.root"
HIGH_PT_BIN_NAMES = ["1200_1750", "1750_2500", "2500_3000"]
IMAGES_DIR = "images"


def main():
    f = ROOT.TFile.Open(MERGED)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {MERGED}")

    edges = array.array('d', [e["min"] for e in ETA_BINS] + [ETA_BINS[-1]["max"]])
    h = ROOT.TH1F("h_muon_count_highpt", "", len(ETA_BINS), edges)
    # Scollegato dal TFile: altrimenti f.Close() lo invalida (e' ancora
    # dentro la directory del file finche' non lo si scollega) e il
    # Draw() dopo la chiusura va in segfault.
    h.SetDirectory(0)

    print("[INFO] Muoni con p_T >= 1.2 TeV (Z aligned + Z' aligned):")
    for i, e in enumerate(ETA_BINS):
        total = 0
        for pt_name in HIGH_PT_BIN_NAMES:
            name = f"h_res_{pt_name}_eta_{e['min']}_{e['max']}"
            hh = f.Get(name)
            if not hh:
                raise RuntimeError(f"Istogramma '{name}' non trovato in {MERGED}")
            total += int(hh.GetEntries())
        h.SetBinContent(i + 1, total)
        print(f"  |eta| [{e['min']}, {e['max']}): {total} muoni")

    f.Close()

    c = ROOT.TCanvas("c_muon_count_highpt", "Muon count vs eta (pT >= 1.2 TeV)", 1000, 700)
    # Margine superiore allargato: altrimenti il titolo scritto a mano (lo
    # stile disabilita il titolo automatico, SetOptTitle(0)) si sovrappone
    # al fattore di scala "x10^3" che ROOT disegna appena sopra il frame.
    c.SetTopMargin(0.12)
    h.SetFillColorAlpha(style.PALETTE[0], 0.5)
    h.SetLineColor(style.PALETTE[0])
    h.SetLineWidth(2)
    h.GetXaxis().SetTitle("|#eta^{truth}|")
    h.GetYaxis().SetTitle("Numero di muoni")
    h.SetTitle("")
    h.SetMinimum(0)
    h.Draw("HIST")

    title = ROOT.TLatex()
    title.SetNDC()
    title.SetTextAlign(21)
    title.SetTextFont(42)
    title.SetTextSize(0.035)
    title.DrawLatex(0.57, 0.965, "Z + Z' aligned combinati -- p_{T}^{truth} #geq 1.2 TeV")

    path = f"{IMAGES_DIR}/muon_count_vs_eta_pt1200"
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"\n[INFO] Plot salvato in {path}.png (.pdf)")


if __name__ == "__main__":
    main()
