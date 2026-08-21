import ROOT

PALETTE = [
    ROOT.kAzure + 2,
    ROOT.kRed + 1,
    ROOT.kGreen + 2,
    ROOT.kOrange + 1,
    ROOT.kMagenta + 1,
    ROOT.kCyan + 2,
    ROOT.kBlack,
]


def apply_style():
    style = ROOT.TStyle("AtlasLike", "ATLAS-like style")

    style.SetCanvasBorderMode(0)
    style.SetCanvasColor(ROOT.kWhite)
    style.SetPadTickX(1)
    style.SetPadTickY(1)
    style.SetPadBorderMode(0)

    style.SetPadTopMargin(0.06)
    style.SetPadBottomMargin(0.14)
    style.SetPadLeftMargin(0.14)
    style.SetPadRightMargin(0.06)

    font = 42
    style.SetTextFont(font)
    style.SetLabelFont(font, "XYZ")
    style.SetTitleFont(font, "XYZ")
    style.SetLabelSize(0.040, "XYZ")
    style.SetTitleSize(0.045, "XYZ")
    style.SetTitleOffset(1.4, "Y")
    style.SetTitleOffset(1.2, "X")

    style.SetOptStat(0)
    style.SetOptTitle(0)
    style.SetOptFit(0)

    style.SetLineWidth(2)
    style.SetHistLineWidth(2)
    style.SetMarkerSize(1.2)

    style.SetPadGridX(False)
    style.SetPadGridY(False)

    ROOT.gROOT.SetStyle("AtlasLike")
    ROOT.gROOT.ForceStyle()
    ROOT.gROOT.SetBatch(True)


def style_histo(h, color, fill=False):
    h.SetLineColor(color)
    h.SetLineWidth(2)
    if fill:
        h.SetFillColorAlpha(color, 0.25)
        h.SetFillStyle(1001)


def make_legend(x1=0.62, y1=0.62, x2=0.90, y2=0.90):
    leg = ROOT.TLegend(x1, y1, x2, y2)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.032)
    return leg
