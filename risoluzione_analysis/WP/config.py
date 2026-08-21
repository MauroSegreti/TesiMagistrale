import math

PT_BINS = [
    {"name": "0_20", "min": 0, "max": 20, "x_center": 13.5, "x_err": 10},
    {"name": "20_30", "min": 20, "max": 30, "x_center": 25.4, "x_err": 5},
    {"name": "30_40", "min": 30, "max": 40, "x_center": 35.2, "x_err": 5},
    {"name": "40_50", "min": 40, "max": 50, "x_center": 44.3, "x_err": 5},
    {"name": "50_80", "min": 50, "max": 80, "x_center": 58.8, "x_err": 15},
    {"name": "80_120", "min": 80, "max": 120, "x_center": 93.9, "x_err": 20},
    {"name": "120_500", "min": 120, "max": 500, "x_center": 160.1, "x_err": 190},
]

# binning per l'efficienza vs eta/phi: uniforme e fine, a differenza dei
# PT_BINS (larghi, pensati per l'RMS della risoluzione) - qui serve vedere
# la transizione barrel-endcap (|eta|~1.05-1.3) e gli eventuali buchi di
# accettanza in phi (regione dei piedi di supporto).
ETA_RANGE = (-2.7, 2.7)
ETA_NBINS = 27

PHI_RANGE = (-math.pi, math.pi)
PHI_NBINS = 32

TREE_NAME = "AnalysisTree"

MAX_EVENTS = -1

# Working point loose/medium/tight: flag booleani cumulativi (muon_Tight
# implica muon_Medium implica muon_Loose), verificato sull'ntupla.
WP_LIST = ["Loose", "Medium", "Tight"]
WP_BRANCH = {
    "Loose": "muon_Loose",
    "Medium": "muon_Medium",
    "Tight": "muon_Tight",
}
ACTIVE_BRANCHES = [
    "muon_pt",
    "truthmuon_pt",
    "truthmuon_eta",
    "truthmuon_phi",
    "muon_truthmuon_index",
    "muon_Loose",
    "muon_Medium",
    "muon_Tight",
]

OUTPUT_ROOT_FILE = "output_wp.root"
IMAGES_DIR = "images"
