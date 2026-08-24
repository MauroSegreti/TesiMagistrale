# Risoluzione in $p_T$ dei muoni — stimatore a quantili (geometria ideale)

Misura della risoluzione in $p_T$ dei muoni, da 20 GeV a 4 TeV, su MC con
geometria ideale (`PerfectAlignment`, Z + 5 Z′). È il riferimento nominale
con cui si confronta poi il campione disallineato in
[`Disallineamento`](../Disallineamento/).

Per ogni muone si calcola la risoluzione in curvatura
$(1/p_T^{reco} - 1/p_T^{truth})/(1/p_T^{truth})$ (curvatura, non $p_T$,
perché è la sagitta — che va come $1/p_T$ — ad avere errore gaussiano), si
riempie una griglia 16 bin di $p_T$ × 6 bin di $|\eta|$, e da ogni istogramma
si estrae $\sigma_{68} = (q_{84} - q_{16})/2$ — l'intervallo interquantile,
scelto al posto di RMS o fit gaussiano perché non assume nessuna forma per
la distribuzione ed è insensibile alle code (RMS ne è dominata, un fit
gaussiano assume che *tutto* l'istogramma, code comprese, sia gaussiano).
Su ogni bin di $|\eta|$ si fitta poi

$$\frac{\sigma_{p_T}}{p_T} = \sqrt{\frac{r_0^2}{p_T^2} + r_1^2 + (r_2\, p_T)^2}$$

con $r_0$ = perdita di energia nel materiale (conta a basso $p_T$), $r_1$ =
multiple scattering (plateau), $r_2$ = risoluzione intrinseca — il termine
dominante ad alto $p_T$ e quello sensibile all'allineamento.

Sono runnati 68 job su 73 (mancano 8, 26, 33, 62 per intoppi di rete e 71,
lo ZeroWidth5000, irraggiungibile).

## Plot

### `plot_res_q68.png` / `.pdf` — il plot principale

Pannello superiore: $\sigma_{68}(p_T)/p_T$ in funzione di $p_T^{truth}$,
scala log-log, un colore per bin di $|\eta|$ (6 curve). I marker sono i
dati — barra d'errore = il maggiore fra l'errore statistico
$\sigma_{68}/\sqrt{2N}$ e il floor sistematico 10% (vedi sotto). Le linee
sono il fit a 3 termini, disegnate su **tutto** il range visibile, anche
oltre gli 800 GeV di `PT_FIT_MAX` dove il fit non è più vincolato dai dati
(estrapolazione, non misura, oltre quel punto).

Pannello inferiore: residuo relativo $(\text{data} - \text{fit})/\text{fit}$
punto per punto. Piatto intorno a zero fino a ~500-800 GeV, poi la curva
estrapolata si stacca in modo sistematico dai punti (fino al -50%) — è
l'effetto delle code non gaussiane ad alto $p_T$, che fanno uscire
$\sigma_{68}$ dalla forma a un solo parametro di scala che la formula
assume (dettagli in "Il fit funziona, ma solo fino a ~800 GeV" sotto).

### `plot_res_gaus.png` / `.pdf` — stesso plot con lo stimatore gaussiano

Identico a `plot_res_q68`, ma con $\sigma$ dal fit gaussiano iterativo
(±2σ dal core, vedi `resolution.py`) al posto di $\sigma_{68}$. Serve solo
da confronto: la differenza fra i parametri di questo fit e di quello
nominale è la sistematica sul metodo riportata nella tabella
"Sistematiche" più sotto.

### `plot_confronto_stimatori.png` — i due stimatori punto per punto

Sovrappone direttamente $\sigma_{68}$ e $\sigma$ gaussiana, **senza fit**:
marker pieni = $\sigma_{68}$, marker vuoti = gaussiana, stesso colore per
bin di $|\eta|$. A basso $p_T$ i due stimatori coincidono (le distribuzioni
sono quasi gaussiane, e per una gaussiana perfetta $\sigma_{68} = \sigma$
esattamente); salendo in $p_T$ i marker vuoti si scostano verso il basso
rispetto ai pieni — la stessa sistematica di metodo vista nel pannello
residui di `plot_res_q68`, qui visibile a occhio senza passare dal fit.

### `table_res_q68.pdf`

Tabella riassuntiva (da `report.py`): per ogni bin di $|\eta|$, numero di
punti entrati nel fit, $r_0$ del fit libero, $\chi^2$/ndf sia per il fit con
$r_0$ libero sia per quello con $r_0$ fissato a 0, e $r_2$ — evidenziato in
blu perché è il numero da confrontare con le prestazioni note di ATLAS.
Righe con $\chi^2$/ndf > 3 sarebbero evidenziate in rosso: qui nessuna,
grazie al floor del 10%.

### `inspect/histos_eta{N}_{lin,log}.png`

Griglia di istogrammi di risoluzione (uno per bin di $p_T$) per il bin di
$|\eta|$ numero N (da `inspect_bins.py`; per ora generati solo per
eta0 ed eta1): ogni pannello mostra l'istogramma con la gaussiana del fit
sovrapposta e tre linee verticali a $q_{16}$, mediana, $q_{84}$. Utile per
vedere a occhio *dove* la distribuzione smette di essere gaussiana — quando
il picco della curva e le linee dei quantili iniziano a divergere.
Versioni in scala lineare e log-y dello stesso bin.
`inspect/log_inspect_eta{N}.txt` è il log numerico corrispondente (entries,
outflow, RMS, $\sigma$ gaussiana, $\sigma_{68}$, rapporto $q_{68}/\text{gaus}$,
asimmetria — un bin di $p_T$ per riga).

### `log_analisi.txt`

Log testuale completo di `analyze.py`: per ogni bin di $|\eta|$, i sei
tentativi di fit multistart (quale seed converge, quale $\chi^2$/ndf, quale
vince), i bin scartati e il motivo, la correlazione $r_0$-$r_1$, e le
sistematiche.

## Risultati

### Le misure sono solide

Per $0.1 \leq |\eta| < 1.05$, il bin con più statistica:

| $p_T$ [GeV] | entries | $\sigma_{68}$ | $q_{68}/\text{gaus}$ | asimmetria |
|---|---|---|---|---|
| 20-30 | 24.4 M | 0.0181 | 1.06 | +0.038 |
| 40-50 | 33.4 M | 0.0203 | 1.05 | +0.028 |
| 100-150 | 933 k | 0.0291 | 1.06 | +0.016 |
| 300-500 | 187 k | 0.0547 | 1.10 | +0.014 |
| 800-1200 | 85 k | 0.0967 | 1.12 | +0.005 |
| 1200-1750 | 184 k | 0.1239 | 1.11 | +0.000 |
| 2500-3000 | 52 k | 0.1551 | 1.11 | −0.000 |
| 3000-4000 | 214 k | 0.2183 | 1.11 | +0.008 |
| 4000-6000 | 11 k | 0.2470 | 1.09 | −0.011 |

Outflow sotto l'1% ovunque, code moderate, asimmetria trascurabile, $\sigma$
monotona su tre ordini di grandezza. I valori riproducono le prestazioni
note di ATLAS per i muoni combinati nel barrel: 2.0% a 45 GeV, 2.9% a 100
GeV, 9.7% a 1 TeV.

L'unica regione con distribuzioni davvero non gaussiane è $|\eta| < 0.1$:
$q_{68}/\text{gaus}$ arriva a 1.71 e l'asimmetria a +0.21 ad alto $p_T$. Lì
la larghezza non è ben definita da un numero solo.

### Il fit: parametri e range di validità

Sul range completo il fit non convergeva a niente di sensato (chi2/ndf da
81 a 83849, residui fino al ±50%, con una forma sistematica — non rumore).
Due cause: (1) con decine di milioni di entries per bin l'errore statistico
su $\sigma_{68}$ è così piccolo che anche uno scarto dello 0.1% fa esplodere
il chi2/ndf; (2) oltre qualche centinaio di GeV le code non gaussiane
iniziano a mangiare nella finestra 16-84%, e $\sigma_{68}$ smette di essere
un parametro di scala pulito.

Rimedio: un floor sistematico relativo sull'errore di $\sigma_{68}$, tarato
al valore che porta chi2/ndf ≈ 1 (con un floor uniforme il chi2/ndf scala
come $1/\text{floor}^2$, quindi i parametri del fit non cambiano — cambia
solo quanto "gridiamo" il disaccordo residuo). Viene **10%**. E il fit
ristretto a $p_T < 800$ GeV (`PT_FIT_MAX`), il punto oltre cui il chi2/ndf
peggiora in modo netto e monotono; i punti oltre 800 GeV restano nel grafico
(sono misure valide) ma non entrano nel fit.

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 36.3 | 0.0181 ± 0.0011 | 0.224 ± 0.012 | 0.58 |
| 0.1 - 1.05 | 0.000 ± 8.98 | 0.0201 ± 0.0010 | 0.126 ± 0.008 | 1.54 |
| 1.05 - 1.3 | 0.000 ± 37.2 | 0.0219 ± 0.0010 | 0.124 ± 0.009 | 0.51 |
| 1.3 - 1.7 | 0.000 ± 32.3 | 0.0305 ± 0.0014 | 0.161 ± 0.011 | 1.68 |
| 1.7 - 2.5 | 0.000 ± 32.5 | 0.0272 ± 0.0011 | 0.089 ± 0.008 | 0.64 |
| 2.5 - 2.8 | 0.223 ± 0.334 | 0.0293 ± 0.0019 | 0.104 ± 0.010 | 0.08 |

L'errore su $r_0$ è enorme rispetto a un floor più stretto (era ±0.001-0.006
al floor 0%, poi ±3-6 al 2%): non è un peggioramento, è che quella
precisione era un artefatto di errori troppo piccoli. Con la sistematica
vera $r_0$ è semplicemente non vincolato ovunque, **anche nel bin
2.5-2.8**, dove con un floor più stretto sembrava significativo.

Sotto ~500-800 GeV il fit segue i dati (residui ~0, banda ±10%). Sopra il
TeV la curva estrapolata diverge dai punti (fino al -50%), atteso: è la
regione dove le code non gaussiane dominano (vedi
`images/plot_res_q68.png`, pannello dei residui).

### Sistematiche

Nominale ($\sigma_{68}$, fit fino a 800 GeV) confrontato con due varianti:
$\sigma$ dal fit gaussiano (stesso range) e fit esteso fino a 2 TeV.

| $\|\eta\|$ | $r_2$ | stat | syst | syst % |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.2236 | 0.0116 | 0.0639 | 29% |
| 0.1 - 1.05 | 0.1257 | 0.0082 | 0.0271 | 22% |
| 1.05 - 1.3 | 0.1239 | 0.0085 | 0.0284 | 23% |
| 1.3 - 1.7 | 0.1606 | 0.0113 | 0.0515 | 32% |
| 1.7 - 2.5 | 0.0893 | 0.0083 | 0.0244 | 27% |
| 2.5 - 2.8 | 0.1041 | 0.0100 | 0.0180 | 17% |

Sistematica scesa dal 40-60% (floor più stretto) al 17-32%: ancora non
piccola (la formula resta un'approssimazione), ma non più "il parametro non
è definito". La colonna "stat" include già il floor del 10%, quindi è
l'incertezza totale del fit, non statistica pura (la statistica pura,
$\sigma_{68}/\sqrt{2N}$, è sub-permille e non è informativa da sola).

### $r_0$: compatibile con zero ovunque

Incluso il bin 2.5-2.8, dove con un floor troppo stretto (2%) sembrava
significativo: $r_0 = 0.223 \pm 0.067$ lì, ora $0.223 \pm 0.334$ col floor
onesto al 10% — stessa stima centrale, ma la significatività era un
artefatto di errori troppo piccoli, non un segnale vero. Coerente con
l'assunzione $r_0 = 0$: il termine di perdita di energia nel materiale conta
solo a $p_T$ basso, e il punto più basso qui è a 25 GeV.

### Regione oltre 800 GeV

Non coperta dal fit: $\sigma_{68}$ misurato lì resta una misura valida
(tabella "le misure sono solide" sopra), ma non è tenuto a seguire la
formula a 3 termini — le code crescenti (asimmetria fino a +0.21,
$q_{68}/\text{gaus}$ fino a 1.71 in $|\eta|<0.1$) la rendono una regione a
parte. Spiegazione fisica plausibile: a bassa energia i muoni perdono
energia quasi solo per ionizzazione (~costante, minimum ionizing particle —
il regime del termine $r_0/p_T$); oltre l'energia critica del muone nel
materiale (ordine del centinaio di GeV — TeV) le perdite radiative
(bremsstrahlung, produzione di coppie) crescono ~linearmente con $p_T$:
processi rari ma con perdite singole grandi, che producono proprio la coda
destra asimmetrica ($p_T^{reco}$ sottostimato) osservata. La soglia
empirica di ~800 GeV dove il fit smette di funzionare è nell'ordine di
grandezza giusto per questo effetto — non una prova, ma coerente.
