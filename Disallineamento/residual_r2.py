"""
r2 residuo: la parte di r2 attribuibile al solo disallineamento, isolata
da r2_nominale sotto l'ipotesi che i due contributi si sommino in
quadratura (indipendenti):

    r2_residual = sqrt(r2_misaligned^2 - r2_nominale^2)

Motivazione: r2 e' un termine di risoluzione (pesa come r2 * pT nella
formula a 3 termini), e le sorgenti di smearing indipendenti si sommano in
quadratura, non linearmente. Se il disallineamento aggiunge uno smearing
extra e scorrelato rispetto a quello gia' presente nel campione nominale
(risoluzione intrinseca del tracciatore con geometria perfetta), allora
il misaligned e' la somma in quadratura dei due:

    r2_misaligned^2 = r2_nominale^2 + r2_disallineamento^2

da cui la formula sopra. E' la stessa logica del closure test su r0/r1
(README, "Closure test dei fit"): li' si verificava che NON si spostassero;
qui si scompone quanto si sposta r2 in "quanto viene messo dal
disallineamento puro".

Per ogni bin di |eta| ricalcola r2 nominale e misaligned con la stessa
sistematica stat+syst di analyze.py (nominale q68, variante gaussiana,
variante range esteso -- vedi Allineamento/README.md, "Sistematiche"),
poi propaga l'errore su sqrt(a^2 - b^2):

    sigma_res = sqrt( (a/res * sigma_a)^2 + (b/res * sigma_b)^2 )

Uso (da Disallineamento/, dopo aver girato analyze.py in entrambe le
cartelle cosi' esistono i due merged_res.root):
    python3 residual_r2.py
"""

import os
import math

import ROOT

from config import PT_FIT_MAX, PT_MAX_VARIANT, ETA_BINS
from compare_alignment import load, NOMINAL_ROOT, MISALIGNED_ROOT
from fitting import build_graphs_and_fits
import style

style.apply_style()

ANADIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ANADIR, "images")


def _r2_with_syst(histos, pt_sums, pt_counts, label):
    """Stessa logica di analyze.py::systematics_table: r2 nominale (q68,
    fino a PT_FIT_MAX) con errore statistico dal fit, sistematica dalla
    variante gaussiana e dalla variante a range esteso sommate in
    quadratura, per ogni bin di |eta|. Ritorna {eta_index: (r2, sigma_comb)}.
    """
    nominal = build_graphs_and_fits(histos, pt_sums, pt_counts, method="q68",
                                    fit_pt_max=PT_FIT_MAX, verbose=False)
    var_gaus = build_graphs_and_fits(histos, pt_sums, pt_counts,
                                     method="gaus", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)
    var_range = build_graphs_and_fits(histos, pt_sums, pt_counts,
                                      method="q68", pt_max=PT_MAX_VARIANT,
                                      verbose=False)

    def r2_of(graphs, e_i):
        for g in graphs:
            if g["eta_index"] == e_i:
                return g["fit"].GetParameter(2) * 1e3, g["fit"].GetParError(2) * 1e3
        return None, None

    out = {}
    print(f"\n=== {label}: r2 nominale + sistematiche (stesso metodo di analyze.py) ===")
    for e_i, e in enumerate(ETA_BINS):
        nom, stat = r2_of(nominal, e_i)
        if nom is None:
            continue
        gau, _ = r2_of(var_gaus, e_i)
        ran, _ = r2_of(var_range, e_i)
        d1 = abs(gau - nom) if gau else 0.0
        d2 = abs(ran - nom) if ran else 0.0
        syst = math.sqrt(d1 ** 2 + d2 ** 2)
        comb = math.sqrt(stat ** 2 + syst ** 2)
        out[e_i] = (nom, comb)
        print(f"  {e['label']:>26}:  r2 = {nom:.4f} +- {stat:.4f} (stat) "
              f"+- {syst:.4f} (syst) = +- {comb:.4f} (comb)")
    return out


def compute_residuals(r2_nom, r2_mis):
    """{eta_index: (r2_res, sigma_res)}, None dove mis <= nom (non definito)."""
    out = {}
    for e_i, (nom, snom) in r2_nom.items():
        if e_i not in r2_mis:
            continue
        mis, smis = r2_mis[e_i]
        if mis ** 2 <= nom ** 2:
            out[e_i] = (None, None)
            continue
        res = math.sqrt(mis ** 2 - nom ** 2)
        sigma_res = math.sqrt((mis / res * smis) ** 2 + (nom / res * snom) ** 2)
        out[e_i] = (res, sigma_res)
    return out


def print_table(r2_nom, r2_mis, residuals):
    print("\n" + "=" * 90)
    print("r2_residual = sqrt(r2_misaligned^2 - r2_nominale^2)   [10^-3 GeV^-1]")
    print("=" * 90)
    print(f"{'|eta| bin':>26}{'r2 nom':>12}{'r2 mis':>12}{'r2 residual':>16}{'% di r2 mis':>14}")
    for e_i, e in enumerate(ETA_BINS):
        if e_i not in residuals:
            continue
        nom, snom = r2_nom[e_i]
        mis, smis = r2_mis[e_i]
        res, sres = residuals[e_i]
        if res is None:
            print(f"{e['label']:>26}{nom:>9.4f}+-{snom:.4f}{mis:>9.4f}+-{smis:.4f}"
                  f"{'non definito (mis <= nom)':>30}")
            continue
        frac = 100 * res / mis
        print(f"{e['label']:>26}{nom:>9.4f}+-{snom:.4f}{mis:>9.4f}+-{smis:.4f}"
              f"{res:>10.4f}+-{sres:.4f}{frac:>10.1f}%")
    print("=" * 90)


def main():
    print(f"[INFO] Nominale:   {NOMINAL_ROOT}")
    print(f"[INFO] Misaligned: {MISALIGNED_ROOT}")

    histos_n, sums_n, counts_n = load(NOMINAL_ROOT)
    histos_m, sums_m, counts_m = load(MISALIGNED_ROOT)

    r2_nom = _r2_with_syst(histos_n, sums_n, counts_n, "Nominale")
    r2_mis = _r2_with_syst(histos_m, sums_m, counts_m, "Misaligned")

    residuals = compute_residuals(r2_nom, r2_mis)
    print_table(r2_nom, r2_mis, residuals)


if __name__ == "__main__":
    main()
