import os
import ROOT
from config import WP_LIST, IMAGES_DIR
from style import PALETTE, style_histo, make_legend


def _save(canvas, basename):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    path = os.path.join(IMAGES_DIR, basename)
    canvas.SaveAs(f"{path}.png")
    canvas.SaveAs(f"{path}.pdf")


def draw_inclusive_overlay(histos_res, suffix=""):
    """Le 3 distribuzioni di risoluzione (Loose/Medium/Tight), normalizzate
    a densita' cosi' da confrontare le forme a parita' di statistica, con
    l'RMS di ciascuna in legenda: e' il plot che mostra che la risoluzione
    non dipende dal WP scelto."""
    c = ROOT.TCanvas(f"c_wp_overlay{suffix}", "Inclusive per WP", 900, 700)
    leg = make_legend(0.58, 0.62, 0.90, 0.90)

    clones = []
    y_max = 0.0
    for i, wp in enumerate(WP_LIST):
        h = histos_res[wp].Clone(f"{histos_res[wp].GetName()}_norm")
        h.SetDirectory(0)
        style_histo(h, PALETTE[i % len(PALETTE)])
        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())
        y_max = max(y_max, h.GetMaximum())
        clones.append(h)

    for i, (wp, h) in enumerate(zip(WP_LIST, clones)):
        h.SetMaximum(y_max * 1.35)
        h.GetXaxis().SetTitle("(1/p_{T}^{reco} - 1/p_{T}^{truth}) / (1/p_{T}^{truth})")
        h.GetYaxis().SetTitle("Fraction of muons / bin")
        h.Draw("HIST" if i == 0 else "HIST SAME")
        rms = histos_res[wp].GetRMS()
        leg.AddEntry(h, f"{wp} (RMS = {rms:.4f})", "l")

    leg.Draw()
    _save(c, f"h_res_wp_overlay{suffix}")
    return c, clones


def make_efficiency(h_pass, h_total, name, title, xaxis_title):
    eff = ROOT.TEfficiency(h_pass, h_total)
    eff.SetName(name)
    # TEfficiency::Paint prende gli assi da qui (";X;Y"), non da GetPaintedGraph
    # dopo il Draw: se lasciato senza ';' eredita il titolo Y da h_total.
    eff.SetTitle(
        f"{title};{xaxis_title};"
        "Efficiency (WP muons / matched reco muons)"
    )
    eff.SetStatisticOption(ROOT.TEfficiency.kFCP)  # Clopper-Pearson
    return eff


# variabile -> (titolo asse x, nome base del file salvato)
_EFF_PLOTS = {
    "pt": ("p_{T}^{truth} [GeV]", "efficiency_vs_pt"),
    "eta": ("#eta^{truth}", "efficiency_vs_eta"),
    "phi": ("#phi^{truth} [rad]", "efficiency_vs_phi"),
}


def build_efficiencies(eff_histos, h_total, wp_list=WP_LIST):
    effs = {}
    for var, (xaxis_title, _) in _EFF_PLOTS.items():
        effs[var] = {
            wp: make_efficiency(
                eff_histos[var][wp], h_total[var], f"eff_{var}_{wp}",
                f"WP efficiency ({wp})", xaxis_title
            )
            for wp in wp_list
        }
    return effs


def draw_efficiency(effs_var, basename, suffix=""):
    """Efficienza del WP (muoni ricostruiti e matchati al truth che
    soddisfano il WP, sul totale dei muoni ricostruiti e matchati) in
    funzione della variabile scelta, per i 3 WP sovrapposti."""
    c = ROOT.TCanvas(f"c_{basename}{suffix}", basename, 900, 700)
    leg = make_legend(0.60, 0.20, 0.90, 0.40)

    for i, wp in enumerate(WP_LIST):
        color = PALETTE[i % len(PALETTE)]
        eff = effs_var[wp]
        eff.SetMarkerColor(color)
        eff.SetLineColor(color)
        eff.SetMarkerStyle(20 + i)
        eff.SetMarkerSize(1.2)
        eff.Draw("AP" if i == 0 else "P SAME")
        leg.AddEntry(eff, wp, "lep")

    c.Update()
    graph = effs_var[WP_LIST[0]].GetPaintedGraph()
    if graph:
        graph.GetYaxis().SetRangeUser(0.0, 1.05)
        c.Modified()
        c.Update()

    leg.Draw()
    c.Update()

    _save(c, f"{basename}{suffix}")
    return c


def save_all_plots(histos_res, effs, suffix=""):
    draw_inclusive_overlay(histos_res, suffix)
    for var, (_, basename) in _EFF_PLOTS.items():
        draw_efficiency(effs[var], basename, suffix)
