"""
Entry point: risoluzione in pT combinando TUTTI i sample (Zp a varie
masse + Z standard) trovati come liste .txt, come richiesto da Luca
("metti insieme tutti gli eventi dei vari samples, inclusa la Z, e
rifai i plot di risoluzione vs pT").

Si possono passare piu' cartelle/file sulla riga di comando: build_chain
li combina tutti nella stessa TChain, quindi la Z standard puo' stare
in una cartella separata dai vari sample Zp.

Uso:
    python3 main.py <cartella_o_file_1> [<cartella_o_file_2> ...]

Esempio (Z standard + Zp separati):
    python3 main.py /path/samples_Zp /path/samples_Z_standard

Un solo run fa tutto: legge la chain UNA volta sola e nello stesso
loop riempie sia gli istogrammi per il fit sia la griglia fine di
statistica (bin_stats) -- non serve piu' lanciare bin_stats.py separatamente
prima. Se pero' vuoi SOLO la diagnostica di statistica (piu' veloce,
niente fit), bin_stats.py resta disponibile standalone.

Genera in output (dentro images/):
- plot_res_vs_pt_3TeV.png / .pdf
- table_res_vs_pt.pdf
- event_distribution_vs_pt.png / .pdf
- table_stats_per_pt_bin.pdf
"""

import sys

from config import TREE_NAME, ETA_BINS, FINE_PT_EDGES
from chain_builder import build_chain
from histograms import build_histogram_grid
from event_loop import process_events
from fitting import build_graphs_and_fits
from plotting import draw_resolution_vs_pt
from report import build_table_pdf
from bin_stats import generate_stats_outputs
import style

style.apply_style()


def main(input_paths):
    histos = build_histogram_grid()

    n_fine = len(FINE_PT_EDGES) - 1
    counts = {e_i: [0] * n_fine for e_i in range(len(ETA_BINS))}

    chain = build_chain(TREE_NAME, *input_paths)

    if chain.GetEntries() == 0:
        print("[ERROR] La chain e' vuota. Verifica i path passati.")
        return

    print("\n[INFO] Inizio loop eventi (fit + diagnostica statistica insieme)...\n")
    filled_muons = process_events(chain, histos, counts)

    if filled_muons == 0:
        print("[ERROR] Nessun muone riempito nei bin. Interrotto.")
        return

    graphs = build_graphs_and_fits(histos)
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
