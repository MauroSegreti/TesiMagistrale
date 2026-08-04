"""
Entry point: RMS della risoluzione in p_T vs |eta_truth|, per bin di p_T
(selezione combinata pT + eta, solo muoni truth prompt IFFType==4).

Uso: python3 main.py <input_path>

Genera in output:
- images/plot_RMS_vs_eta.png / .pdf
- images/table_RMS_vs_eta.pdf  (stessa tabella stampata a console)
"""

import sys

from config import TREE_NAME
from chain_builder import build_chain
from histograms import build_histogram_grid
from event_loop import process_events
from plotting import build_rms_graphs, draw_rms_vs_eta
from report import build_table_pdf
import style

style.apply_style()


def main(input_path):
    histos = build_histogram_grid()
    chain = build_chain(TREE_NAME, input_path)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons, total_prompt = process_events(chain, histos)

    print(f"\n[INFO] Muoni prompt processati = {total_prompt}")
    print(f"[INFO] Muoni riempiti negli istogrammi = {filled_muons}")

    graphs, results = build_rms_graphs(histos)
    draw_rms_vs_eta(graphs)
    build_table_pdf(results)

    print("\n[INFO] Plot salvato in images/plot_RMS_vs_eta.png (.pdf)")
    print("[INFO] Tabella salvata in images/table_RMS_vs_eta.pdf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
