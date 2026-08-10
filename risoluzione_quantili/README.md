# Risoluzione in $p_T$ dei muoni — stimatore a quantili

Misuro la risoluzione in $p_T$ dei muoni da 20 GeV a 4 TeV combinando Z e Z′ su
MC con geometria ideale (`PerfectAlignment`). È il riferimento nominale contro
cui confronterò i campioni disallineati.

Seconda versione dell'analisi: rispetto a `risoluzione_pt_zprime` cambia il
metodo con cui estraggo la larghezza — **interquantili al 68% invece del fit
gaussiano**, su indicazione di Luca.

## Cosa misuro

Per ogni muone ricostruito risalgo al truth associato e calcolo la risoluzione in
curvatura:

$$\frac{1/p_T^{reco} - 1/p_T^{truth}}{1/p_T^{truth}} = \frac{p_T^{truth}}{p_T^{reco}} - 1$$


È la variabile giusta perché il tracciamento misura la sagitta, che va come
$1/p_T$: è la curvatura ad avere errore gaussiano, non il $p_T$.

Riempio una griglia 16 × 6 (bin di $p_T$ × bin di $|\eta|$), da ogni istogramma
estraggo $\sigma_{68} = (q_{84} - q_{16})/2$ con errore $\sigma_{68}/\sqrt{2N}$, e
fitto l'andamento con

$$\frac{\sigma_{p_T}}{p_T} = \sqrt{\frac{r_0^2}{p_T^2} + r_1^2 + (r_2 \, p_T)^2}$$

Solo muoni truth prompt (`IFFType == 4`).


### I tre termini

**$r_0/p_T$** — fluttuazioni della perdita di energia nel materiale. Costante in
valore assoluto, quindi pesa come $1/p_T$: conta solo a basso $p_T$.

**$r_1$** — multiple scattering. Scala con $p_T$ come la misura stessa, quindi dà
un contributo relativo costante: è il plateau.

**$r_2 \, p_T$** — risoluzione intrinseca. La sagitta va come $1/p_T$, quindi con
un errore di posizione fisso l'errore relativo cresce linearmente: domina in
cima. È il termine sensibile all'allineamento.

## Perché Z e Z′ insieme

Non sono due campioni da confrontare: sono entrambi MC, passati per la stessa
simulazione dello stesso rivelatore con la stessa geometria. Sono pezzi della
**stessa** misura, giusto?. La Z dà muoni a $\approx m_Z/2$, ogni Z′ a $\approx m/2$;
insieme coprono tutto lo spettro.


Se ho capito benne, la catena di produzione è: generatore → depositi di
energia con Geant4 → digitizzazione → ricostruzione. È la **ricostruzione** a
prendere in input la geometria, nominale o sbagliata. In entrambi i campioni i
muoni attraversano lo stesso rivelatore: quello che cambia è dove il software
crede che siano le camere. Il disallineamento è in 3D, non solo lungo $z$.

## Struttura: due fasi

**`fill.py`** gira nei job condor, uno per file: riempie la griglia e salva
`output_res.root`. Nessun fit.

**`analyze.py`** gira dopo, una volta: `hadd`, diagnostica, fit, plot, tabelle,
sistematiche.

Il fit non può stare nei job perché la funzione si aggiusta su tutti i punti in
$p_T$ insieme, e quei punti vengono da campioni diversi.

## Come giro

Niente download: le liste `.root.txt` contengono URL `root://` e i job leggono
via XRootD. Il proxy VOMS va messo su AFS — `/tmp` è locale alla macchina e lo
schedd (`bigbird15`) non lo vede, quindi i job finirebbero in `HOLD`.

```bash
setupATLAS
voms-proxy-init -voms atlas --valid 24:00
cp /tmp/x509up_u$(id -u) $HOME/x509up
chmod 600 $HOME/x509up
export X509_USER_PROXY=$HOME/x509up

./gen_jobs.sh                 # 68 file Z + 5 Z' = 73 job
condor_submit condorSub.sub
```

Test su un job Z′ prima di lanciare tutto (i primi 68 sono la Z):

```bash
sed 's|jobs/do_\*.sh|jobs/do_68.sh|' condorSub.sub > condorTest.sub
condor_submit condorTest.sub
```

Analisi:

```bash
python3 analyze.py /eos/user/m/masegret/risoluzione_quantili_out
python3 inspect_bins.py merged_res.root 1
```

## I file

**`config.py`** — 16 bin di $p_T$ (fino a 6 TeV) e 6 di $|\eta|$.

**`chain_builder.py`** — `TChain` da file, lista Rucio o cartella.

**`histograms.py`** — griglia di istogrammi sul $p_T$ e
rispetto ai bin di $\eta$.

**`event_loop.py`** — truth matching, selezione prompt, riempimento.

**`resolution.py`** — i due stimatori: `sigma_q68` nominale, `sigma_gaus` per il
confronto. Riporta anche l'asimmetria
$[(q_{84}-\text{med}) - (\text{med}-q_{16})]/(q_{84}-q_{16})$.

**`fitting.py`** — grafici e fit, con `method` e `pt_max` selezionabili.

**`plotting.py`** — plot log-log con pannello dei residui, più il confronto
diretto fra punti q68 e gaussiani.

**`report.py`** — tabella PDF dei parametri.

**`inspect_bins.py`** — guarda i singoli punti prima di fittarli: entries,
outflow, RMS, $\sigma$ gaussiana, $\sigma_{68}$, il rapporto e l'asimmetria; salva
la griglia degli istogrammi con la gaussiana e le linee a $q_{16}$, mediana,
$q_{84}$.

**`gen_jobs.sh` / `condorSub.sub`** — job e submit.

## Risultati

runnati 68 job su 73 (mancano 8, 26, 33, 62 per intoppi di rete e 71,
il ZeroWidth5000 non raggiungibile vai a capì...).

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
monotona su tre ordini di grandezza.

E soprattutto i valori riproducono le prestazioni note di ATLAS per i muoni
combinati nel barrel: 2.0% a 45 GeV, 2.9% a 100 GeV, 9.7% a 1 TeV sempre se non ho aperto una pagina di 30 anni fa... 

L'unica regione con distribuzioni davvero non gaussiane è $|\eta| < 0.1$: $q_{68}/\text{gaus}$ arriva a 1.71 e l'asimmetria a $+0.21$ ad
alto $p_T$. Lì la larghezza non è ben definita da un numero solo.

### Il fit invece non funziona santa pace

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 0.003 | 0.0178 | 0.214 | 7591 |
| 0.1 - 1.05 | 0.000 ± 0.001 | 0.0193 | 0.090 | 83849 |
| 1.05 - 1.3 | 0.000 ± 0.006 | 0.0214 | 0.090 | 6213 |
| 1.3 - 1.7 | 0.000 ± 0.003 | 0.0287 | 0.142 | 22828 |
| 1.7 - 2.5 | 0.000 ± 0.003 | 0.0258 | 0.103 | 12683 |
| 2.5 - 2.8 | **0.322 ± 0.002** | 0.0283 | 0.112 | **81** |

I residui arrivano a $+40\%$ intorno ai 200 GeV e $-45\%$ sopra il TeV...
### Sistematiche

Nominale ($\sigma_{68}$, range completo) confrontato con due varianti: $\sigma$
dal fit gaussiano, e range limitato a 2 TeV.

| $\|\eta\|$ | $r_2$ | stat | syst | syst % |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.2140 | 0.0003 | 0.0873 | 41% |
| 0.1 - 1.05 | 0.0899 | 0.0001 | 0.0530 | 59% |
| 1.05 - 1.3 | 0.0895 | 0.0002 | 0.0355 | 40% |
| 1.3 - 1.7 | 0.1422 | 0.0002 | 0.0388 | 27% |
| 1.7 - 2.5 | 0.1031 | 0.0002 | 0.0140 | 14% |
| 2.5 - 2.8 | 0.1118 | 0.0007 | 0.0162 | 15% |

Syst viene del 40-60% quindi penso che il parametro non è ben definito con questa
parametrizzazione...penso è

### $r_0$

Torna esattamente zero nei bin 0-4, al limite inferiore, e i fit con $r_0$ libero
e fissato danno $r_1$ e $r_2$ identici: il termine conta solo a $p_T$ basso e il
punto più basso è a 25 GeV.

Nel bin 2.5-2.8 invece $r_0 = 0.322 \pm 0.002$ GeV è significativo e il fit libero
è nettamente migliore (81 contro 1330), con correlazione $r_0$-$r_1$ di $-0.884$.
Coerente con l'assunzione $r_0 = 0$ che vale solo dove c'è
l'inner detector, e che finisce a 2.5.

