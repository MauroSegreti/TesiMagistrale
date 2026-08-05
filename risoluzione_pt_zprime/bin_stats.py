"""
Tool diagnostico (richiesta esplicita di Luca): mostra la statistica
(numero di entries) disponibile per bin di eta x pT, PRIMA di decidere
il binning finale in config.py.

Puo' essere usato in due modi:
1. STANDALONE, per un check veloce prima di lanciare il fit vero
   (es. con MAX_EVENTS ridotto in config.py per un test rapido):
       python3 bin_stats.py <cartella_o_file_1> [<cartella_o_file_2> ...]
2. Le funzioni compute_stats/print_table sono importate direttamente
   da main.py, che calcola la stessa statistica NELLO STESSO loop del
   fit (vedi event_loop.py) -- cosi' un solo "python3 main.py" produce
   sia i risultati del fit sia questa diagnostica, senza rileggere la
   chain due volte.
"""

import sys

from config import TREE_NAME, ETA_BINS, PROMPT_IFF_TYPE, PT_TRUTH_MAX, MAX_EVENTS, MIN_ENTRIES_FOR_FIT, FINE_PT_EDGES
from chain_builder import build_chain
from bin_stats_report import plot_event_distribution, build_stats_table_pdf
import style


def compute_stats(chain):
    """Ritorna dict {indice_bin_eta: [entries_bin_pt_0, entries_bin_pt_1, ...]}.
    Usata solo in modalita' standalone -- quando main.py gira, questa stessa
    struttura viene gia' riempita da event_loop.process_events nello stesso
    loop del fit."""
    n_pt = len(FINE_PT_EDGES) - 1
    counts = {e_i: [0] * n_pt for e_i in range(len(ETA_BINS))}

    for i, entry in enumerate(chain):
        if MAX_EVENTS > 0 and i >= MAX_EVENTS:
            break
        if i % 100000 == 0 and i > 0:
            print(f"[INFO] Processati {i} eventi")

        muon_pt = entry.muon_pt
        truth_pt = entry.truthmuon_pt
        truth_eta = entry.truthmuon_eta
        truth_index = entry.muon_truthmuon_index
        truth_type = entry.truthmuon_IFFType

        for j in range(len(muon_pt)):
            idx = truth_index[j]
            if idx < 0 or idx >= len(truth_pt):
                continue
            if truth_type[idx] != PROMPT_IFF_TYPE:
                continue

            pt_true = truth_pt[idx] / 1000.0
            eta_true = abs(truth_eta[idx])

            if pt_true <= 0 or pt_true > PT_TRUTH_MAX:
                continue

            for e_i, e in enumerate(ETA_BINS):
                if e["min"] <= eta_true < e["max"]:
                    for p_i in range(n_pt):
                        if FINE_PT_EDGES[p_i] <= pt_true < FINE_PT_EDGES[p_i + 1]:
                            counts[e_i][p_i] += 1
                            break
                    break

    return counts


def print_table(counts):
    n_pt = len(FINE_PT_EDGES) - 1
    col_w = 12

    header = "pT [GeV]".ljust(16) + "".join(f"eta bin {e_i}".rjust(col_w) for e_i in range(len(ETA_BINS)))
    print("\n=== Statistica (entries) per bin fine di pT x bin di eta ===")
    print("(* = sotto MIN_ENTRIES_FOR_FIT, da unire a un bin vicino)\n")
    print(header)

    for p_i in range(n_pt):
        row_label = f"{FINE_PT_EDGES[p_i]:.0f}-{FINE_PT_EDGES[p_i+1]:.0f}".ljust(16)
        cells = []
        for e_i in range(len(ETA_BINS)):
            n = counts[e_i][p_i]
            mark = "*" if n < MIN_ENTRIES_FOR_FIT else ""
            cells.append(f"{n}{mark}".rjust(col_w))
        print(row_label + "".join(cells))

    print("\n[INFO] Usa questa tabella per scegliere i bordi dei bin finali in")
    print("       config.py: unisci bin adiacenti dove la statistica e' bassa,")
    print("       tienili separati dove c'e' abbastanza statistica per un RMS stabile.")


def generate_stats_outputs(counts):
    """Stampa la tabella a console e genera i due PDF/PNG diagnostici.
    Richiamata sia da bin_stats.py standalone sia da main.py."""
    print_table(counts)
    plot_event_distribution(counts, FINE_PT_EDGES)
    build_stats_table_pdf(counts, FINE_PT_EDGES, ETA_BINS, MIN_ENTRIES_FOR_FIT)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 bin_stats.py <cartella_o_file_1> [<cartella_o_file_2> ...]\n")
        sys.exit(1)

    style.apply_style()

    chain = build_chain(TREE_NAME, *sys.argv[1:])
    if chain.GetEntries() == 0:
        print("[ERROR] La chain e' vuota. Verifica i path passati.")
        sys.exit(1)

    counts = compute_stats(chain)
    generate_stats_outputs(counts)
