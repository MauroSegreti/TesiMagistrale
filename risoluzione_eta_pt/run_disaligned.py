"""
Ripete identica l'analisi di main.py (griglia RMS pT x eta, plot,
tabella, plot RMS vs pT per bin di eta) ma sul campione Z disallineato
(MisAligned_MC, 26 file, letti via XRootD in un'unica TChain).

Stessa selezione (muoni truth prompt, IFFType==4), stessa variabile di
risoluzione, stessi PT_BINS/ETA_BINS di config.py -- cambia solo
l'input. Output in images2/ (per non toccare i risultati del campione
allineato in images/), root file merged_eta_disaligned.root.

Uso: python3 run_disaligned.py
"""

import ROOT

from config import TREE_NAME, PT_BINS, ETA_BINS
from chain_builder import build_chain
from histograms import build_histogram_grid
from event_loop import process_events
import plotting
import report
import plot_rms_vs_pt_per_eta as pt_eta
import style

style.apply_style()

# Tutti i moduli di plotting scrivono in un IMAGES_DIR di modulo: lo
# ripuntiamo su images2 cosi' non tocchiamo i plot del campione allineato.
plotting.IMAGES_DIR = "images2"
report.IMAGES_DIR = "images2"
pt_eta.IMAGES_DIR = "images2"

INPUT_LIST = ("/afs/cern.ch/user/m/masegret/MisAligned_MC/"
              "user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu."
              "MCP_TESTNTUP.mc23e_MSmisalign_ANALYSIS.root.txt")
OUTPUT_ROOT_FILE = "merged_eta_disaligned.root"


def save_histograms(histos, path=OUTPUT_ROOT_FILE):
    out = ROOT.TFile(path, "RECREATE")
    n = 0
    for p in PT_BINS:
        for h in histos[p["name"]]:
            h.Write()
            n += 1
    out.Close()
    print(f"[INFO] {n} istogrammi salvati in {path}")


def main():
    histos = build_histogram_grid()
    chain = build_chain(TREE_NAME, INPUT_LIST)

    print("\n[INFO] Inizio loop eventi (Z disallineato, 26 file via XRootD)...\n")
    filled_muons, total_prompt = process_events(chain, histos)

    print(f"\n[INFO] Muoni prompt processati = {total_prompt}")
    print(f"[INFO] Muoni riempiti negli istogrammi = {filled_muons}")

    save_histograms(histos)

    graphs, results = plotting.build_rms_graphs(histos)
    plotting.draw_rms_vs_eta(graphs)
    plotting.draw_eta_overlay(histos)
    report.build_table_pdf(results)

    f = ROOT.TFile.Open(OUTPUT_ROOT_FILE)
    for eta in ETA_BINS:
        points = pt_eta.load_points(f, eta)
        pt_eta.draw(points, eta)
    f.Close()

    print("\n[INFO] Fatto. Plot in images2/, istogrammi in "
          f"{OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    main()
