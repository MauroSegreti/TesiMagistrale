from config import (PT_BINS, ETA_BINS, MAX_EVENTS, PROMPT_IFF_TYPE,
                    PT_TRUTH_MAX)


def process_events(chain, histos, h_pt_sum, h_pt_count):
    counter_total_muons = 0
    counter_idx_valid = 0
    counter_prompt = 0
    filled_muons = 0

    n_total = chain.GetEntries()

    if MAX_EVENTS > 0 and MAX_EVENTS < n_total:
        stride = max(1, n_total // MAX_EVENTS)
        indices = range(0, n_total, stride)
        print(f"[INFO] Sottocampionamento uniforme: 1 evento ogni {stride} "
              f"-> ~{len(indices)} eventi su {n_total}")
    else:
        indices = range(n_total)
        print(f"[INFO] Lettura completa: {n_total} eventi")

    n_read = 0
    for i in indices:
        chain.GetEntry(i)
        n_read += 1
        if n_read % 100000 == 0:
            print(f"[INFO] Processati {n_read} eventi (entry {i}/{n_total})",
                  flush=True)

        muon_pt = chain.muon_pt
        truth_pt = chain.truthmuon_pt
        truth_eta = chain.truthmuon_eta
        truth_index = chain.muon_truthmuon_index
        truth_type = chain.truthmuon_IFFType

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
                            h_pt_sum.Fill(e_i + 0.5, p_i + 0.5, pt_true)
                            h_pt_count.Fill(e_i + 0.5, p_i + 0.5)
                            filled_muons += 1
                            break
                    break

    print("\n=== Statistiche ===")
    print(f"Eventi letti: {n_read} (su {n_total} nella chain)")
    print(f"Muoni totali (candidati reco): {counter_total_muons}")
    print(f"Truth match validi: {counter_idx_valid}")
    print(f"Prompt (IFFType == {PROMPT_IFF_TYPE}): {counter_prompt}")
    print(f"Muoni riempiti nei bin: {filled_muons}\n")

    return filled_muons
