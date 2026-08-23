"""
Entry point: RMS della risoluzione in p_T vs |eta_truth|, per bin di p_T
(selezione combinata pT + eta, solo muoni truth prompt IFFType==4).

Uso: python3 main.py <input_path>

Genera in output:
- output_eta.root          griglia completa di istogrammi (serve per hadd)
- images/plot_RMS_vs_eta.png / .pdf
- images/plot_eta_overlay.png / .pdf  (overlay dei 6 bin di eta,
  normalizzati e inclusivi su pT -- solo muoni prompt)
- images/table_RMS_vs_eta.pdf  (stessa tabella stampata a console)
"""

import sys
import ROOT

from config import TREE_NAME, PT_BINS, ETA_BINS
from chain_builder import build_chain
from histograms import build_histogram_grid
from event_loop import process_events
from plotting import build_rms_graphs, draw_rms_vs_eta, draw_eta_overlay
from report import build_table_pdf
import style

style.apply_style()

OUTPUT_ROOT_FILE = "output_eta.root"


def save_histograms(histos, path=OUTPUT_ROOT_FILE):
    """
    Salva tutta la griglia pT x eta su file. Serve per poter unire con hadd
    gli output dei job condor: senza questo ogni job produrrebbe solo i suoi
    plot parziali, non combinabili.
    """
    out = ROOT.TFile(path, "RECREATE")
    n = 0
    for p in PT_BINS:
        for h in histos[p["name"]]:
            h.Write()
            n += 1
    out.Close()
    print(f"[INFO] {n} istogrammi salvati in {path}")


def main(input_path):
    histos = build_histogram_grid()
    chain = build_chain(TREE_NAME, input_path)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons, total_prompt = process_events(chain, histos)

    print(f"\n[INFO] Muoni prompt processati = {total_prompt}")
    print(f"[INFO] Muoni riempiti negli istogrammi = {filled_muons}")

    save_histograms(histos)

    graphs, results = build_rms_graphs(histos)
    draw_rms_vs_eta(graphs)
    draw_eta_overlay(histos)
    build_table_pdf(results)

    print("\n[INFO] Plot salvato in images/plot_RMS_vs_eta.png (.pdf)")
    print("[INFO] Plot overlay eta salvato in images/plot_eta_overlay.png (.pdf)")
    print("[INFO] Tabella salvata in images/table_RMS_vs_eta.pdf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
