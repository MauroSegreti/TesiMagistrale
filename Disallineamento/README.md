# Risoluzione in $p_T$ dei muoni — campioni MS-misaligned

Stessa identica misura di [`Allineamento`](../Allineamento/) — stesso
binning, stesso stimatore ($\sigma_{68}$), stesso fit a 3 termini, stesso
codice — ma sui campioni con **geometria disallineata** (tag
`mc23e_MSmisalign`) invece di `PerfectAlignment`. Per metodo e formula, vedi
il README di `Allineamento`; qui il focus è sul confronto fra i due
campioni.

| DSID | campione |
|---|---|
| 601190 | Z → μμ (Powheg+Pythia8 AZNLO) |
| 801862 | Z′ ZeroWidth 500 GeV |
| 801863 | Z′ ZeroWidth 1000 GeV |
| 801864 | Z′ ZeroWidth 3000 GeV |
| 801865 | Z′ ZeroWidth 5000 GeV |
| 801866 | Z′ ZeroWidth 8000 GeV |

Primo giro: 31 job sottomessi (26 Zmumu + 5 Z′), 30 completati — `job_24`
(un file Zmumu su MPCDF) è andato in errore per un redirect XRootD, non un
problema della misura. Nessun bin scartato per outflow.

## Plot

### `plot_res_q68.png`/`.pdf`, `plot_res_gaus.png`/`.pdf`, `plot_confronto_stimatori.png`, `table_res_q68.pdf`

Stessi plot/tabella di [`Allineamento`](../Allineamento/), prodotti dallo
stesso codice (`plotting.py`, `report.py`) ma sui dati misaligned — vedi la
sezione "Plot" del README di `Allineamento` per la spiegazione di ciascuno.
`log_analisi.txt` è l'equivalente log testuale di `analyze.py` su questo
campione.

### `plot_confronto_allineamento.png` / `.pdf` — nominale vs misaligned

Generato da `compare_alignment.py`. Pannello superiore: le curve nominale
(marker pieni, linea continua) e misaligned (marker vuoti, linea
tratteggiata) sovrapposte sullo stesso grafico $\sigma_{68}(p_T)/p_T$ vs
$p_T^{truth}$, stesso colore per bin di $|\eta|$, entrambe fittate con la
stessa formula a 3 termini.

Il pannello inferiore **non è un residuo** ma il rapporto continuo fra le
due curve di fit, misaligned/nominale, sull'intersezione dei due range
validi:

$$\frac{\sigma_{68}^{mis}(p_T)}{\sigma_{68}^{nom}(p_T)} = \frac{f^{mis}(p_T)}{f^{nom}(p_T)}$$

dove $f^{nom}$, $f^{mis}$ sono le due curve di fit valutate con i rispettivi
parametri $r_0, r_1, r_2$ — non i punti dati, la curva continua.

A basso $p_T$ il rapporto è vicino a 1 (dominano $r_0$ e $r_1$, che il
disallineamento non tocca — vedi closure test sotto); sale con $p_T$ perché
il termine sensibile alla geometria è $r_2\, p_T$, che cresce linearmente; e
si stabilizza al plateau asintotico $r_2^{mis}/r_2^{nom}$ (stessi numeri
della tabella "Confronto diretto" sotto) quando $r_2\, p_T$ domina sugli
altri due termini. Il plateau più alto (~4×) è per $2.5 \le |\eta| < 2.8$,
il più basso (~1.4×) per $0.1 \le |\eta| < 1.05$: la curva teal si stacca
visibilmente prima e più in alto delle altre.

### `table_closure_test.pdf`

Generata da `closure_test.py`: per ogni bin di $|\eta|$, i tre parametri del
fit libero — nominale, misaligned, differenza in $N\sigma$ — affiancati per
$r_0$, $r_1$, $r_2$. Le celle di $r_0$/$r_1$ con $N\sigma > 2$ sarebbero
evidenziate in rosso (qui nessuna lo è): vedi "Closure test dei fit" sotto
per i numeri e l'interpretazione.

## Risultati

### Fit (q68, fino a 800 GeV, floor 10% ereditato dal nominale)

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 45.2 | 0.0182 ± 0.0014 | 0.311 ± 0.015 | 0.16 |
| 0.1 - 1.05 | 0.000 ± 30.9 | 0.0209 ± 0.0011 | 0.192 ± 0.011 | 0.67 |
| 1.05 - 1.3 | 0.001 ± 38.3 | 0.0229 ± 0.0014 | 0.270 ± 0.014 | 0.29 |
| 1.3 - 1.7 | 0.000 ± 45.3 | 0.0290 ± 0.0016 | 0.283 ± 0.016 | 0.20 |
| 1.7 - 2.5 | 0.000 ± 49.4 | 0.0269 ± 0.0015 | 0.278 ± 0.015 | 0.05 |
| 2.5 - 2.8 | 0.404 ± 0.347 | 0.0309 ± 0.0044 | 0.430 ± 0.024 | 0.06 |

Chi2/ndf tutti $\lesssim 1$, anche troppo bassi: il floor del 10% è stato
calibrato sulla dispersione punto-punto del *nominale*, che ha statistica
molto più alta (73 file contro 31). Qui probabilmente è più largo del
necessario — da ricalibrare (stesso procedimento del nominale) se serve un
$\chi^2$/ndf realistico invece che solo "il fit converge bene".

### Fit con $r_0$ fissato a 0

Stesso fit (`fit_fixed0`) rifatto imponendo $r_0 = 0$ invece di lasciarlo
libero, come per il nominale (vedi `Allineamento/README.md`):

| $\|\eta\|$ | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|
| 0.0 - 0.1 | 0.0182 ± 0.0014 | 0.3114 ± 0.0150 | 0.14 |
| 0.1 - 1.05 | 0.0209 ± 0.0011 | 0.1916 ± 0.0108 | 0.59 |
| 1.05 - 1.3 | 0.0229 ± 0.0014 | 0.2704 ± 0.0142 | 0.25 |
| 1.3 - 1.7 | 0.0290 ± 0.0016 | 0.2834 ± 0.0158 | 0.17 |
| 1.7 - 2.5 | 0.0269 ± 0.0015 | 0.2777 ± 0.0153 | 0.04 |
| 2.5 - 2.8 | 0.0331 ± 0.0021 | 0.4251 ± 0.0222 | 0.10 |

Anche qui $r_1$ e $r_2$ restano praticamente identici al fit con $r_0$
libero: coerente col fatto che $r_0$ è compatibile con zero in ogni bin
anche in questo campione (vedi il closure test sotto, dove $r_0$ resta
sotto 1 sigma di differenza rispetto al nominale).

### Confronto diretto con il nominale

Stesso identico metodo e binning, quindi $r_2$ è confrontabile punto per
punto: la sola differenza è la geometria.

| $\|\eta\|$ | $r_2$ nominale | $r_2$ misaligned | rapporto |
|---|---|---|---|
| 0.0 - 0.1 | 0.224 ± 0.065 | 0.311 ± 0.051 | 1.4× |
| 0.1 - 1.05 | 0.126 ± 0.028 | 0.192 ± 0.027 | 1.5× |
| 1.05 - 1.3 | 0.124 ± 0.030 | 0.270 ± 0.030 | 2.2× |
| 1.3 - 1.7 | 0.161 ± 0.053 | 0.283 ± 0.028 | 1.8× |
| 1.7 - 2.5 | 0.089 ± 0.026 | 0.278 ± 0.030 | 3.1× |
| 2.5 - 2.8 | 0.104 ± 0.021 | 0.430 ± 0.062 | 4.1× |

($r_2$ in $10^{-3}$ GeV$^{-1}$, errori stat+syst in quadratura; vedi
`images/plot_confronto_allineamento.png` per la curva completa)

**La degradazione da disallineamento cresce con $|\eta|$**: da ~1.4× nel
barrel centrale a ~4× nel forward (2.5-2.8). Fisicamente sensato: oltre
$|\eta| = 2.5$ le tracce sono standalone nel muon spectrometer (niente inner
detector), quindi meno misure ridondanti per compensare l'errore di
posizione delle camere disallineate. Il barrel centrale, dove $r_2$ è già il
più piccolo dei due casi, è anche il più protetto in termini relativi.

### Closure test dei fit

Il confronto sopra si basa solo su $r_2$: da solo non basta a escludere che
stia confrontando due fit fatti in modo diverso invece di due geometrie
diverse. Test più stringente: controllare anche $r_0$ ed $r_1$, che *non*
dovrebbero dipendere dalla geometria del muon spectrometer ($r_0$ = perdita
di energia nel materiale, $r_1$ = multiple scattering — entrambi
indifferenti a dove il software crede che siano le camere). Se il fit li
vede spostarsi in modo significativo fra nominale e misaligned, c'è
qualcosa che non va nel confronto (binning diverso, fit degenere, bug), non
un vero effetto fisico.

`closure_test.py` calcola, per ogni bin di $|\eta|$, la differenza fra i
parametri liberi dei due fit in unità di sigma combinata:

$$\sigma_{\text{comb}} = \sqrt{\sigma_{\text{nom}}^2 + \sigma_{\text{mis}}^2}
\qquad
N\sigma = \frac{|r_{\text{mis}} - r_{\text{nom}}|}{\sigma_{\text{comb}}}$$

(propagazione standard sotto l'ipotesi di fit scorrelati — ragionevole:
campioni statisticamente indipendenti). Le celle con $N\sigma > 2$ su $r_0$
o $r_1$ segnalerebbero un closure test fallito.

| $\|\eta\|$ | $r_0$ $N\sigma$ | $r_1$ $N\sigma$ | $r_2$ $N\sigma$ |
|---|---|---|---|
| 0.0 - 0.1 | 0.00 | 0.06 | 4.63 |
| 0.1 - 1.05 | 0.00 | 0.50 | 4.84 |
| 1.05 - 1.3 | 0.00 | 0.60 | 8.84 |
| 1.3 - 1.7 | 0.00 | 0.67 | 6.32 |
| 1.7 - 2.5 | 0.00 | 0.15 | 10.84 |
| 2.5 - 2.8 | 0.38 | 0.35 | 12.64 |

Il closure test passa ovunque: $r_0$ ed $r_1$ restano sotto 1 sigma in tutti
i bin (su $r_0$ la compatibilità è in parte banale — è comunque non
vincolato dal fit — ma $r_1$ è ben misurato e torna entro 0.67 sigma
ovunque). $r_2$ invece si sposta fra 4.6 e 12.6 sigma in ogni bin: il
comportamento atteso, essendo l'unico termine sensibile alla geometria
delle camere. Il fatto che sia l'unico a muoversi, sempre nella stessa
direzione (peggiora, mai migliora) e in modo crescente con $|\eta|$ come il
rapporto sopra, è la controprova che l'effetto è reale e non un artefatto
del fit.

### $r_2$ residuo: quanto ci mette il disallineamento da solo

Il confronto e il closure test sopra dicono *che* $r_2$ peggiora e *che* è
l'unico a farlo, ma non isolano un numero per "quanto smearing aggiunge il
disallineamento da solo", separato dalla risoluzione intrinseca già
presente con la geometria perfetta. Serve un'ipotesi in più: $r_2$ è un
termine di risoluzione, e sorgenti di smearing **indipendenti** si sommano
in quadratura, non linearmente. Se il disallineamento aggiunge uno smearing
extra e scorrelato,

$$\left(r_2^{\text{misaligned}}\right)^2 = \left(r_2^{\text{nominale}}\right)^2 + \left(r_2^{\text{residual}}\right)^2
\quad\Longrightarrow\quad
r_2^{\text{residual}} = \sqrt{\left(r_2^{\text{misaligned}}\right)^2 - \left(r_2^{\text{nominale}}\right)^2}$$

con l'errore propagato dalla stessa forma (regola della catena su
$f=\sqrt{a^2-b^2}$):

$$\sigma_{\text{residual}} = \sqrt{\left(\frac{r_2^{\text{mis}}}{r_2^{\text{res}}} \times \sigma_{\text{mis}}\right)^2 + \left(\frac{r_2^{\text{nom}}}{r_2^{\text{res}}} \times \sigma_{\text{nom}}\right)^2}$$

dove $\sigma_{\text{nom}}$, $\sigma_{\text{mis}}$ sono gli stessi errori
stat+syst in quadratura della tabella "Confronto diretto" sopra. Calcolato
da `residual_r2.py`:

| $\|\eta\|$ | $r_2$ nominale | $r_2$ misaligned | $r_2$ residuo | % di $r_2$ misaligned |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.224 ± 0.065 | 0.311 ± 0.051 | 0.217 ± 0.099 | 70% |
| 0.1 - 1.05 | 0.126 ± 0.028 | 0.192 ± 0.027 | 0.145 ± 0.043 | 76% |
| 1.05 - 1.3 | 0.124 ± 0.030 | 0.270 ± 0.030 | 0.240 ± 0.037 | 89% |
| 1.3 - 1.7 | 0.161 ± 0.053 | 0.283 ± 0.028 | 0.233 ± 0.050 | 82% |
| 1.7 - 2.5 | 0.089 ± 0.026 | 0.278 ± 0.030 | 0.263 ± 0.033 | 95% |
| 2.5 - 2.8 | 0.104 ± 0.021 | 0.430 ± 0.063 | 0.418 ± 0.065 | 97% |

($r_2$ in $10^{-3}$ GeV$^{-1}$)

Il contributo puro del disallineamento domina già a partire da
$1.05 \le |\eta| < 1.3$ (89% del misaligned totale) e sale fino al 97% nel
forward (2.5-2.8): coerente col fatto che è lì che il rapporto
misaligned/nominale è più alto (tabella "Confronto diretto"). Nel barrel
centrale ($0.1 \le |\eta| < 1.05$) resta comunque maggioritario (76%) ma con
errore relativo più grande (~30%): lì $r_2^{\text{nom}}$ e
$r_2^{\text{mis}}$ sono più vicini fra loro, e la sottrazione in quadratura
amplifica l'errore relativo — la stessa ragione per cui $\sigma_f$ va come
$r_2^{\text{mis}}/r_2^{\text{res}}$ nella formula sopra: più
$r_2^{\text{res}}$ è piccolo rispetto a $r_2^{\text{mis}}$, più l'errore si
gonfia.

L'ipotesi di indipendenza è la stessa che sta dietro il closure test: se
$r_0$ ed $r_1$ non si spostano fra i due campioni (verificato sopra), è
plausibile che anche gli altri contributi allo smearing — perdita di
energia nel materiale, multiple scattering — restino invariati e scorrelati
dal termine di allineamento, l'assunzione che rende valida la somma in
quadratura qui.
