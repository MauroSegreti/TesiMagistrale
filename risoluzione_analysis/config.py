PT_BINS = [
    {"name": "0_20", "min": 0, "max": 20, "x_center": 13.5, "x_err": 10},
    {"name": "20_30", "min": 20, "max": 30, "x_center": 25.4, "x_err": 5},
    {"name": "30_40", "min": 30, "max": 40, "x_center": 35.2, "x_err": 5},
    {"name": "40_50", "min": 40, "max": 50, "x_center": 44.3, "x_err": 5},
    {"name": "50_80", "min": 50, "max": 80, "x_center": 58.8, "x_err": 15},
    {"name": "80_120", "min": 80, "max": 120, "x_center": 93.9, "x_err": 20},
    {"name": "120_500", "min": 120, "max": 500, "x_center": 160.1, "x_err": 190},
]

TREE_NAME = "AnalysisTree"

MAX_EVENTS = -1

PROMPT_IFF_TYPE = 4

ACTIVE_BRANCHES = [
    "muon_pt",
    "truthmuon_pt",
    "truthmuon_IFFType",
    "muon_truthmuon_index",
]

OUTPUT_ROOT_FILE = "output_risoluzione.root"
IMAGES_DIR = "images"
