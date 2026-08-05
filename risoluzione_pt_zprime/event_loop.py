"""
Loop sugli eventi. Dato che chain_builder.py aggiunge alla stessa
TChain tutti i path passati, "combinare tutti i sample" (richiesta di
Luca) e' gia' garantito a monte: qui il loop semplicemente scorre
tutti gli eventi della chain combinata, senza distinguere da quale
sample provengano.

Se viene passato anche 'counts' (griglia fine per bin_stats.py), lo
riempie NELLO STESSO loop degli istogrammi per il fit -- cosi' un solo
python3 main.py basta per avere sia i risultati del fit sia la
diagnostica di statistica, senza rileggere la chain due volte (utile
soprattutto quando i dati sono remoti via XRootD, dove la lettura e'
il collo di bottiglia).
"""

from config import PT_BINS, ETA_BINS, MAX_EVENTS, PROMPT_IFF_TYPE, PT_TRUTH_MAX, FINE_PT_EDGES


def process_events(chain, histos, counts=None):
    counter_total_muons = 0
    counter_idx_valid = 0
    counter_prompt = 0
    filled_muons = 0

    n_fine = len(FINE_PT_EDGES) - 1

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
            counter_total_muons += 1
            idx = truth_index[j]
            if idx < 0 or idx >= len(truth_pt):
                continue
            counter_idx_valid += 1

            if truth_type[idx] != PROMPT_IFF_TYPE:
                continue
            counter_prompt += 1

            pt_reco = muon_pt[j] / 1000.0
            pt_true = truth_pt[idx] / 1000.0
            eta_true = abs(truth_eta[idx])

            if pt_reco <= 0 or pt_true <= 0 or pt_true > PT_TRUTH_MAX:
                continue

            res = (pt_true / pt_reco) - 1.0

            for e_i, e in enumerate(ETA_BINS):
                if e["min"] <= eta_true < e["max"]:
                    for p_i, p in enumerate(PT_BINS):
                        if p["min"] <= pt_true < p["max"]:
                            histos[e_i][p_i].Fill(res)
                            filled_muons += 1
                            break

                    if counts is not None:
                        for fp_i in range(n_fine):
                            if FINE_PT_EDGES[fp_i] <= pt_true < FINE_PT_EDGES[fp_i + 1]:
                                counts[e_i][fp_i] += 1
                                break

                    break

    print("\n=== Statistiche ===")
    print(f"Muoni totali (candidati reco): {counter_total_muons}")
    print(f"Truth match validi: {counter_idx_valid}")
    print(f"Prompt (IFFType == 4): {counter_prompt}")
    print(f"Muoni riempiti nei bin: {filled_muons}\n")

    return filled_muons
