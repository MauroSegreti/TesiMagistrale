"""
Loop sugli eventi: seleziona solo i muoni truth "prompt" (IFFType == 4,
richiesta di Luca) e li smista nell'istogramma giusto in base al bin
di pT e al bin di |eta| a cui appartengono (selezione combinata di Marco).
"""

from config import PT_BINS, ETA_BINS, MAX_EVENTS, PROMPT_IFF_TYPE


def process_events(chain, histos):
    filled_muons = 0
    total_prompt = 0

    for i, entry in enumerate(chain):
        if MAX_EVENTS > 0 and i >= MAX_EVENTS:
            break

        if i % 50000 == 0:
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

            # Solo muoni truth "prompt"
            if truth_type[idx] != PROMPT_IFF_TYPE:
                continue
            total_prompt += 1

            pt_reco = muon_pt[j] / 1000.0
            pt_true = truth_pt[idx] / 1000.0
            eta_true = abs(truth_eta[idx])

            if pt_reco <= 0 or pt_true <= 0:
                continue

            res = (pt_true / pt_reco) - 1.0

            # Trova il bin di pT giusto, poi al suo interno il bin di eta giusto
            for p in PT_BINS:
                if p["min"] <= pt_true < p["max"]:
                    for e_i, e in enumerate(ETA_BINS):
                        if e["min"] <= eta_true < e["max"]:
                            histos[p["name"]][e_i].Fill(res)
                            filled_muons += 1
                            break
                    break

    return filled_muons, total_prompt
