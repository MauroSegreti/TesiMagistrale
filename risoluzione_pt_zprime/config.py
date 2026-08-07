PT_BINS = [
    {"name": "20_30", "min": 20, "max": 30, "mean": 25.0},
    {"name": "30_40", "min": 30, "max": 40, "mean": 35.0},
    {"name": "40_50", "min": 40, "max": 50, "mean": 45.0},
    {"name": "50_70", "min": 50, "max": 70, "mean": 60.0},
    {"name": "70_100", "min": 70, "max": 100, "mean": 85.0},
    {"name": "100_150", "min": 100, "max": 150, "mean": 125.0},
    {"name": "150_200", "min": 150, "max": 200, "mean": 175.0},
    {"name": "200_300", "min": 200, "max": 300, "mean": 250.0},
    {"name": "300_500", "min": 300, "max": 500, "mean": 400.0},
    {"name": "500_800", "min": 500, "max": 800, "mean": 650.0},
    {"name": "800_1200", "min": 800, "max": 1200, "mean": 1000.0},
    {"name": "1200_1750", "min": 1200, "max": 1750, "mean": 1475.0},
    {"name": "1750_2500", "min": 1750, "max": 2500, "mean": 2125.0},
    {"name": "2500_3000", "min": 2500, "max": 3000, "mean": 2750.0},
]

ETA_BINS = [
    {"min": 0.0, "max": 0.1, "label": "0.0 #leq |#eta| < 0.1"},
    {"min": 0.1, "max": 1.05, "label": "0.1 #leq |#eta| < 1.05"},
    {"min": 1.05, "max": 1.3, "label": "1.05 #leq |#eta| < 1.3"},
    {"min": 1.3, "max": 1.7, "label": "1.3 #leq |#eta| < 1.7"},
    {"min": 1.7, "max": 2.5, "label": "1.7 #leq |#eta| < 2.5"},
    {"min": 2.5, "max": 2.8, "label": "2.5 #leq |#eta| < 2.8"},
]

TREE_NAME = "AnalysisTree"
MAX_EVENTS = -1

PROMPT_IFF_TYPE = 4
PT_TRUTH_MAX = 3000.0

EXPECTED_R1 = 0.025
EXPECTED_R2 = 3.0e-4
N_WINDOW_SIGMA = 6.0
MIN_WINDOW = 0.12
HIST_N_BINS = 240

# Fattore di allargamento della finestra per bin di eta. Ad alto |eta| le
# tracce sono stand-alone (niente inner detector) e le code sono molto piu'
# larghe: con fattore 1 il 3-7% degli eventi finiva in over/underflow e tutti
# i bin di 2.5-2.8 venivano scartati.
ETA_WINDOW_SCALE = [1.0, 1.0, 1.0, 1.5, 1.5, 4.0]

MIN_ENTRIES_FOR_FIT = 200

PLOT_X_MIN = 15
PLOT_X_MAX = 3500

OUTPUT_ROOT_FILE = "output_res.root"
