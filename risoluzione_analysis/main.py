"""
Entry point dell'analisi.
Uso: python3 main.py <input_path>

Genera in output:
- output_risoluzione.root  (tutti gli istogrammi + i due TGraphErrors)
- h_res_all.png / h_res_all_prompt.png
- plot_range_<bin>.png / plot_range_<bin>_prompt.png
- rms_vs_pt.png / rms_vs_pt_prompt.png
"""

import sys
import ROOT

from config import TREE_NAME, OUTPUT_ROOT_FILE
from chain_builder import build_chain
from histograms import build_histogram_set
from event_loop import process_events
from plotting import make_rms_graph, save_all_plots
import style

style.apply_style()


def main(input_path):
    # Istogrammi: versione inclusiva + versione "prompt" (IFFType==4)
    h_all, histos_pt = build_histogram_set()
    h_all_prompt, histos_pt_prompt = build_histogram_set(suffix="_prompt")

    chain = build_chain(TREE_NAME, input_path)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons, filled_muons_prompt = process_events(
        chain, h_all, histos_pt, h_all_prompt, histos_pt_prompt
    )

    out_file = ROOT.TFile(OUTPUT_ROOT_FILE, "RECREATE")

    h_all.Write()
    for h in histos_pt.values():
        h.Write()
    h_all_prompt.Write()
    for h in histos_pt_prompt.values():
        h.Write()

    graph = make_rms_graph(
        histos_pt, "g_rms_vs_pt",
        "p_{T} Resolution; p_{T}^{truth} [GeV]; RMS"
    )
    graph.Write()

    graph_prompt = make_rms_graph(
        histos_pt_prompt, "g_rms_vs_pt_prompt",
        "p_{T} Resolution (prompt); p_{T}^{truth} [GeV]; RMS"
    )
    graph_prompt.Write()

    save_all_plots(h_all, histos_pt, graph)
    save_all_plots(h_all_prompt, histos_pt_prompt, graph_prompt, suffix="_prompt")

    out_file.Close()

    print("\n[INFO] Muoni riempiti (inclusivo) =", filled_muons)
    print("[INFO] Muoni riempiti (prompt, IFFType==4) =", filled_muons_prompt)
    print("[INFO] File ROOT salvato:", OUTPUT_ROOT_FILE)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
