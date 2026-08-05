"""
Configurazione per l'analisi combinata di risoluzione in pT su tutti
i sample (Zp a varie masse + Z standard), come richiesto da Luca:
"metti insieme tutti gli eventi dei vari samples (inclusa la Z) e
rifai i plot di risoluzione vs pT".

L'input_path va passato come cartella contenente TUTTI i file .txt
(liste Rucio) dei sample da combinare -- Z inclusa. chain_builder.py
li aggiunge tutti alla stessa TChain, quindi la "combinazione" avviene
semplicemente includendo il file .txt della Z nella stessa cartella
degli altri.
"""

# Bin di pT estesi fino a 3 TeV (i sample Zp ad alta massa producono
# muoni con pT molto più alto dei sample Z standard)
# Binning "di partenza": molto piu' fine ad alto pT rispetto a prima
# (che aveva solo 3 bin enormi sopra i 120 GeV: 120-500, 500-1500,
# 1500-3000). Da rifinire con bin_stats.py una volta viste le entries
# reali per bin sui sample combinati -- unisci i bin dove la statistica
# e' troppo bassa per un RMS stabile, tienili separati dove c'e' abbastanza
# statistica.
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

# NOTA: qui uso 1.05 come nel tuo script -- nel progetto risoluzione_eta_pt
# avevamo invece usato 1.01 (dal commento dettagliato di Luca sui bin).
# Verifica con Luca quale dei due e' quello giusto e allinea entrambi i
# progetti di conseguenza.
ETA_BINS = [
    {"min": 0.0, "max": 0.1, "label": "0.0 #leq |#eta| < 0.1"},
    {"min": 0.1, "max": 1.05, "label": "0.1 #leq |#eta| < 1.05"},
    {"min": 1.05, "max": 1.3, "label": "1.05 #leq |#eta| < 1.3"},
    {"min": 1.3, "max": 1.7, "label": "1.3 #leq |#eta| < 1.7"},
    {"min": 1.7, "max": 2.5, "label": "1.7 #leq |#eta| < 2.5"},
    {"min": 2.5, "max": 2.8, "label": "2.5 #leq |#eta| < 2.8"},
]

TREE_NAME = "AnalysisTree"
MAX_EVENTS = -1  # nessun limite: processa tutti gli eventi di tutti i sample

PROMPT_IFF_TYPE = 4
PT_TRUTH_MAX = 3000.0  # taglio superiore su pT truth, in GeV

# Un bin con troppo poche entries non viene incluso nel fit (fit instabile)
MIN_ENTRIES_FOR_FIT = 5

# Range dell'asse x (log) nel plot finale
PLOT_X_MIN = 15
PLOT_X_MAX = 3500

# Griglia fine di riferimento per bin_stats.py (indipendente dal binning
# "finale" PT_BINS sopra). Vive qui, non in bin_stats.py, cosi' main.py
# puo' calcolare la statistica diagnostica nello STESSO loop del fit,
# senza dover rileggere la chain una seconda volta.
FINE_PT_EDGES = [15, 20, 25, 30, 40, 50, 65, 80, 100, 120, 150, 200, 250, 300,
                  400, 500, 650, 800, 1000, 1250, 1500, 1750, 2000, 2500, 3000]
