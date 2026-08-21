from config import MAX_EVENTS, WP_LIST, WP_BRANCH


def process_events(chain, histos_res, eff_histos, h_total):
    filled_muons = 0
    wp_branch_names = [WP_BRANCH[wp] for wp in WP_LIST]

    for i, entry in enumerate(chain):
        if MAX_EVENTS > 0 and i >= MAX_EVENTS:
            break

        if i % 100000 == 0:
            print(f"[INFO] Processati {i} eventi", flush=True)

        muon_pt = entry.muon_pt
        truthmuon_pt = entry.truthmuon_pt
        truthmuon_eta = entry.truthmuon_eta
        truthmuon_phi = entry.truthmuon_phi
        truth_index = entry.muon_truthmuon_index
        wp_flags = [getattr(entry, name) for name in wp_branch_names]

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

            eta_truth = truthmuon_eta[idx_truth]
            phi_truth = truthmuon_phi[idx_truth]

            res_curv = (pt_truth / pt_reco) - 1.0
            filled_muons += 1
            h_total["pt"].Fill(pt_truth)
            h_total["eta"].Fill(eta_truth)
            h_total["phi"].Fill(phi_truth)

            for wp, flags in zip(WP_LIST, wp_flags):
                # i branch WP sono vector<char>: PyROOT restituisce ogni
                # elemento come str di un carattere, e bool('\x00') e' True
                # in Python (stringa non vuota) -> serve ord() per il valore.
                if ord(flags[j]):
                    histos_res[wp].Fill(res_curv)
                    eff_histos["pt"][wp].Fill(pt_truth)
                    eff_histos["eta"][wp].Fill(eta_truth)
                    eff_histos["phi"][wp].Fill(phi_truth)

    return filled_muons
