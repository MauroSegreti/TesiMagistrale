import ROOT
from config import (PT_BINS, ETA_BINS, EXPECTED_R1, EXPECTED_R2,
                    N_WINDOW_SIGMA, HIST_N_BINS, MIN_WINDOW,
                    ETA_WINDOW_SCALE)


def expected_sigma(pt):
    return (EXPECTED_R1 ** 2 + (EXPECTED_R2 * pt) ** 2) ** 0.5


def window_for(pt, scale=1.0):
    return scale * max(MIN_WINDOW, N_WINDOW_SIGMA * expected_sigma(pt))


def build_histogram_grid():
    histos = {}
    for e_i, e in enumerate(ETA_BINS):
        scale = ETA_WINDOW_SCALE[e_i]
        histos[e_i] = []
        for p in PT_BINS:
            w = window_for(p["mean"], scale)
            h = ROOT.TH1F(f"h_res_eta_{e_i}_{p['name']}", "",
                          HIST_N_BINS, -w, w)
            h.Sumw2()
            h.SetDirectory(0)
            histos[e_i].append(h)
    return histos


def build_pt_accumulators():
    n_eta = len(ETA_BINS)
    n_pt = len(PT_BINS)
    h_sum = ROOT.TH2D("h_pt_sum", "", n_eta, 0, n_eta, n_pt, 0, n_pt)
    h_count = ROOT.TH2D("h_pt_count", "", n_eta, 0, n_eta, n_pt, 0, n_pt)
    h_sum.SetDirectory(0)
    h_count.SetDirectory(0)
    return h_sum, h_count


def read_pt_means(h_sum, h_count):
    pt_sums = {}
    pt_counts = {}
    for e_i in range(len(ETA_BINS)):
        pt_sums[e_i] = [h_sum.GetBinContent(e_i + 1, p_i + 1)
                        for p_i in range(len(PT_BINS))]
        pt_counts[e_i] = [h_count.GetBinContent(e_i + 1, p_i + 1)
                          for p_i in range(len(PT_BINS))]
    return pt_sums, pt_counts


def print_window_summary():
    print("\n=== Finestra istogramma (semi-larghezza) per bin di pT x eta ===")
    header = f"{'bin pT':>12} {'sigma att.':>11}"
    for e_i, e in enumerate(ETA_BINS):
        header += f"  {'%.1f-%.1f' % (e['min'], e['max']):>10}"
    print(header)
    print(f"{'':>12} {'scale ->':>11}" +
          "".join(f"  {ETA_WINDOW_SCALE[e_i]:>10.1f}"
                  for e_i in range(len(ETA_BINS))))
    for p in PT_BINS:
        s = expected_sigma(p["mean"])
        row = f"{p['name']:>12} {s:11.4f}"
        for e_i in range(len(ETA_BINS)):
            row += f"  {window_for(p['mean'], ETA_WINDOW_SCALE[e_i]):>10.3f}"
        print(row)
    print()
