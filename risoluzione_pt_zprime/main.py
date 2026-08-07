"""
Entry point: risoluzione in pT combinando TUTTI i sample (Zp a varie
masse + Z standard).

Uso:
    python3 main.py <cartella_o_file_1> [<cartella_o_file_2> ...]

Esempio (Z standard + Zp separati):
    python3 main.py /path/samples_Zp /path/samples_Z_standard

Genera in output (dentro images/):
- plot_res_vs_pt_3TeV.png / .pdf
- table_res_vs_pt.pdf
- event_distribution_vs_pt.png / .pdf
- table_stats_per_pt_bin.pdf
"""

import sys

from config import TREE_NAME, ETA_BINS, PT_BINS, FINE_PT_EDGES
from chain_builder import build_chain
from histograms import build_histogram_grid, print_window_summary
from event_loop import process_events
from fitting import build_graphs_and_fits
from plotting import draw_resolution_vs_pt
from report import build_table_pdf
from bin_stats import generate_stats_outputs
import style

style.apply_style()


def main(input_paths):
    print_window_summary()

    histos = build_histogram_grid()

    n_fine = len(FINE_PT_EDGES) - 1
    n_pt = len(PT_BINS)
    counts = {e_i: [0] * n_fine for e_i in range(len(ETA_BINS))}

    # Somme dei pT truth per usare il pT MEDIO del bin come ascissa
    # del fit invece del centro geometrico (vedi fitting.py).
    pt_sums = {e_i: [0.0] * n_pt for e_i in range(len(ETA_BINS))}
    pt_counts = {e_i: [0] * n_pt for e_i in range(len(ETA_BINS))}

    chain = build_chain(TREE_NAME, *input_paths)

    if chain.GetEntries() == 0:
        print("[ERROR] La chain e' vuota. Verifica i path passati.")
        return

    print("\n[INFO] Inizio loop eventi (fit + diagnostica statistica insieme)...\n")
    filled_muons = process_events(chain, histos, counts, pt_sums, pt_counts)

    if filled_muons == 0:
        print("[ERROR] Nessun muone riempito nei bin. Interrotto.")
        return

    # Confronto centro geometrico vs pT medio effettivo: rende visibile
    # di quanto era spostata l'ascissa nella versione precedente.
    print("=== Ascissa: centro geometrico vs pT medio effettivo ===")
    print(f"{'bin pT':>14} {'centro':>9} {'medio':>9} {'shift':>8}")
    for p_i, p in enumerate(PT_BINS):
        tot_n = sum(pt_counts[e_i][p_i] for e_i in range(len(ETA_BINS)))
        tot_s = sum(pt_sums[e_i][p_i] for e_i in range(len(ETA_BINS)))
        if tot_n == 0:
            continue
        mean_eff = tot_s / tot_n
        print(f"{p['name']:>14} {p['mean']:9.0f} {mean_eff:9.0f} "
              f"{100*(mean_eff/p['mean']-1):+7.1f}%")
    print()

    graphs = build_graphs_and_fits(histos, pt_sums, pt_counts)
    if not graphs:
        print("[ERROR] Nessun bin di eta con abbastanza punti validi.")
        return

    draw_resolution_vs_pt(graphs)
    build_table_pdf(graphs)

    print("\n[INFO] Genero anche la diagnostica di statistica per bin...\n")
    generate_stats_outputs(counts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <cartella_o_file_1> [<cartella_o_file_2> ...]\n")
        print("Si possono passare piu' path per combinare sample diversi")
        print("(es. una cartella con la Z standard + una con i vari Zp).\n")
        sys.exit(1)

    main(sys.argv[1:])
