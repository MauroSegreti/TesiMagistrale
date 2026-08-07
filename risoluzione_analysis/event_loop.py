from config import PT_BINS, MAX_EVENTS, PROMPT_IFF_TYPE


def _find_bin(pt_truth):
    for b in PT_BINS:
        if b["min"] <= pt_truth < b["max"]:
            return b["name"]
    return None


def process_events(chain, h_all, histos_pt, h_all_prompt, histos_pt_prompt):
    filled_muons = 0
    filled_muons_prompt = 0

    for i, entry in enumerate(chain):
        if MAX_EVENTS > 0 and i >= MAX_EVENTS:
            break

        if i % 100000 == 0:
            print(f"[INFO] Processati {i} eventi", flush=True)

        muon_pt = entry.muon_pt
        truthmuon_pt = entry.truthmuon_pt
        truthmuon_ifftype = entry.truthmuon_IFFType
        truth_index = entry.muon_truthmuon_index

        if len(muon_pt) == 0:
            continue

        for j in range(len(muon_pt)):
            idx_truth = truth_index[j]
            if idx_truth < 0 or idx_truth >= len(truthmuon_pt):
                continue

            pt_reco = muon_pt[j] / 1000.0
            pt_truth = truthmuon_pt[idx_truth] / 1000.0

            if pt_reco <= 0 or pt_truth <= 0:
                continue

            res_curv = (pt_truth / pt_reco) - 1.0
            bin_name = _find_bin(pt_truth)

            h_all.Fill(res_curv)
            filled_muons += 1
            if bin_name is not None:
                histos_pt[bin_name].Fill(res_curv)

            if truthmuon_ifftype[idx_truth] == PROMPT_IFF_TYPE:
                h_all_prompt.Fill(res_curv)
                filled_muons_prompt += 1
                if bin_name is not None:
                    histos_pt_prompt[bin_name].Fill(res_curv)

    return filled_muons, filled_muons_prompt
