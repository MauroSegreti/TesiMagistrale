import sys
import ROOT

from config import TREE_NAME, OUTPUT_ROOT_FILE, ACTIVE_BRANCHES
from chain_builder import build_chain, enable_branches
from histograms import build_histogram_set
from event_loop import process_events
from plotting import make_rms_graph, save_all_plots
import style

style.apply_style()


def main(input_path):
    h_all, histos_pt = build_histogram_set()
    h_all_prompt, histos_pt_prompt = build_histogram_set(suffix="_prompt")

    chain = build_chain(TREE_NAME, input_path)
    enable_branches(chain, ACTIVE_BRANCHES)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons, filled_muons_prompt = process_events(
        chain, h_all, histos_pt, h_all_prompt, histos_pt_prompt
    )

    graph = make_rms_graph(
        histos_pt, "g_rms_vs_pt",
        "p_{T} Resolution; p_{T}^{truth} [GeV]; RMS"
    )
    graph_prompt = make_rms_graph(
        histos_pt_prompt, "g_rms_vs_pt_prompt",
        "p_{T} Resolution (prompt); p_{T}^{truth} [GeV]; RMS"
    )

    out_file = ROOT.TFile(OUTPUT_ROOT_FILE, "RECREATE")
    h_all.Write()
    for h in histos_pt.values():
        h.Write()
    h_all_prompt.Write()
    for h in histos_pt_prompt.values():
        h.Write()
    graph.Write()
    graph_prompt.Write()
    out_file.Close()

    save_all_plots(h_all, histos_pt, graph)
    save_all_plots(h_all_prompt, histos_pt_prompt, graph_prompt, suffix="_prompt")

    print("\n[INFO] Muoni riempiti (inclusivo) =", filled_muons)
    print("[INFO] Muoni riempiti (prompt, IFFType==4) =", filled_muons_prompt)
    print("[INFO] File ROOT salvato:", OUTPUT_ROOT_FILE)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
