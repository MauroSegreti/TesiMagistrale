"""
Per ogni bin di eta costruisce il TGraphErrors di RMS vs pT (su tutti
i bin di pT, con statistica combinata da tutti i sample), poi lo fitta
con la formula completa a 3 termini della risoluzione in pT:

    sigma_pT / pT = sqrt( r0^2/pT^2 + r1^2 + (r2 * pT)^2 )

- r0/pT domina a BASSO pT (fluttuazioni di energia depositata)
- r1 e' il termine costante (multiple scattering)
- r2 * pT domina ad ALTO pT (disallineamento/potere di curvatura)

MULTI-START: con un solo tentativo di fit (un solo punto di partenza)
MINUIT convergeva spesso su una soluzione degenere con r1 schiacciato
a 0 -- che elimina il tratto piatto centrale della curva e la
trasforma in una parabola/V che non rispecchia i dati (niente plateau
da multiple scattering). Non e' un problema della formula: e' il fit
che si blocca in un minimo locale sbagliato. Qui si prova il fit da
piu' punti di partenza diversi e si tiene quello con il chi2/ndf
migliore -- tecnica standard per aggirare i minimi locali di un fit
non lineare.

Per ogni bin di eta viene fatto anche un SECONDO fit, con r0 fissato
a 0 (richiesta di Luca: confrontare la qualita' del fit libero contro
quella del fit senza il termine a basso pT). I due TF1 risultanti
sono salvati come "fit" (libero) e "fit_fixed0" (r0 = 0) nel dict
restituito per ogni bin di eta, insieme a "n_points" (quanti bin di
pT hanno statistica sufficiente ed entrano nel fit) -- questi tre
campi sono quelli che report.py si aspetta di trovare.
"""

import array
import ROOT
from config import PT_BINS, ETA_BINS, MIN_ENTRIES_FOR_FIT, PLOT_X_MIN, PLOT_X_MAX
from style import PALETTE

FIT_FORMULA = "sqrt(([0]/x)*([0]/x) + [1]*[1] + ([2]*x)*([2]*x))"

# Punti di partenza diversi (r0, r1, r2) da provare per ogni fit.
# r1 parte da valori vicini al plateau osservato nei dati (~0.02-0.03)
# invece che da un valore arbitrario, per aiutare il fit a "vedere"
# subito il tratto piatto invece di ignorarlo e collassarlo a 0.
_SEEDS = [
    (0.1, 0.025, 0.0001),
    (1.0, 0.030, 0.0001),
    (3.0, 0.020, 0.0002),
    (0.01, 0.035, 0.0005),
    (5.0, 0.028, 0.00005),
    (0.5, 0.022, 0.00015),
]


def _make_fit(name, seed, fix_r0):
    """Crea un TF1 con la formula standard, inizializzato al seed dato.
    Se fix_r0=True, il parametro r0 (indice 0) viene fissato a 0 invece
    di essere lasciato libero -- r1 e r2 restano agli stessi indici in
    entrambi i casi, cosi' i due fit restano confrontabili parametro
    per parametro."""
    r0_seed, r1_seed, r2_seed = seed
    fit_func = ROOT.TF1(name, FIT_FORMULA, PLOT_X_MIN, PLOT_X_MAX)
    fit_func.SetParameters(r0_seed, r1_seed, r2_seed)
    fit_func.SetParLimits(0, 0, 50)   # r0 >= 0: fisicamente non puo' essere negativo
    fit_func.SetParLimits(1, 0, 1)
    fit_func.SetParLimits(2, 0, 1)
    if fix_r0:
        fit_func.FixParameter(0, 0)
    return fit_func


def _fit_multistart(graph, name_prefix, color, fix_r0):
    """Prova il fit da tutti i seed in _SEEDS, tiene quello con chi2/ndf
    migliore. Ritorna (fit_migliore, lista_chi2ndf_per_tentativo)."""
    best_fit = None
    best_chi2ndf = float("inf")
    attempts = []

    for i, seed in enumerate(_SEEDS):
        fit_func = _make_fit(f"{name_prefix}_try{i}", seed, fix_r0)
        # "N": non allega la funzione al grafico (evita che tutti i
        # tentativi, anche quelli falliti, vengano disegnati insieme)
        graph.Fit(fit_func, "QRN")

        ndf = fit_func.GetNDF()
        chi2 = fit_func.GetChisquare()
        chi2ndf = chi2 / ndf if ndf > 0 else float("inf")
        attempts.append(chi2ndf)

        if chi2ndf < best_chi2ndf:
            best_chi2ndf = chi2ndf
            best_fit = fit_func

    best_fit.SetLineColor(color)
    best_fit.SetLineWidth(2)
    return best_fit, attempts


def build_graphs_and_fits(histos):
    graphs = []

    for e_i, e in enumerate(ETA_BINS):
        x = array.array('d')
        y = array.array('d')
        ex = array.array('d')
        ey = array.array('d')

        for p_i, p in enumerate(PT_BINS):
            h = histos[e_i][p_i]
            if h.GetEntries() < MIN_ENTRIES_FOR_FIT:
                continue

            x.append(p["mean"])
            ex.append((p["max"] - p["min"]) / 2.0)
            y.append(h.GetRMS())
            ey.append(h.GetRMSError())

        if len(x) == 0:
            print(f"[WARNING] Nessun bin con statistica sufficiente per eta bin {e_i}, salto")
            continue

        n_points = len(x)
        color = PALETTE[e_i % len(PALETTE)]
        g = ROOT.TGraphErrors(n_points, x, y, ex, ey)
        g.SetName(f"g_eta_{e_i}")
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.SetMarkerStyle(20)
        g.SetLineWidth(2)

        print(f"\n[INFO] Fit multi-start eta bin {e_i} ({e['label']}) -- r0 libero:")
        fit_free, attempts_free = _fit_multistart(g, f"fit_eta_{e_i}_free", color, fix_r0=False)
        print(f"       chi2/ndf per tentativo: {[f'{v:.2f}' for v in attempts_free]}"
              f"  -> migliore: seed #{attempts_free.index(min(attempts_free))}")

        print(f"[INFO] Fit multi-start eta bin {e_i} ({e['label']}) -- r0 fissato a 0:")
        fit_fixed0, attempts_fixed0 = _fit_multistart(g, f"fit_eta_{e_i}_fix0", color, fix_r0=True)
        print(f"       chi2/ndf per tentativo: {[f'{v:.2f}' for v in attempts_fixed0]}"
              f"  -> migliore: seed #{attempts_fixed0.index(min(attempts_fixed0))}")

        graphs.append({
            "graph": g,
            "fit": fit_free,
            "fit_fixed0": fit_fixed0,
            "eta": e,
            "n_points": n_points,
        })

    return graphs