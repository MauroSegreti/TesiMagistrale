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

### Perché $\sigma_{68}$ e non RMS o fit gaussiano

Uso l'intervallo interquantile e non RMS o un fit gaussiano perché non
assume nessuna forma per la distribuzione: usa solo il 16° e l'84°
percentile, quindi non è sensibile a quello che succede nelle code, a
differenza della RMS (dominata dagli outlier) o di un fit gaussiano (che
assume che *tutto* l'istogramma sia gaussiano, core e code). Per una
distribuzione perfettamente gaussiana coincide esattamente con la
deviazione standard — $q_{84} - q_{16} = 2\sigma$, quindi
$(q_{84}-q_{16})/2 = \sigma$ — quindi dove i due metodi si applicano bene
danno la stessa risposta (vedi `images/plot_confronto_stimatori.png`); dove
la distribuzione si allontana dalla gaussiana (code asimmetriche ad alto
$p_T$, vedi sotto), $\sigma_{68}$ resta un numero ben definito mentre un
fit gaussiano no. L'errore $\sigma_{68}/\sqrt{2N}$ è l'errore standard di
uno stimatore di quantile: cala con la statistica come qualsiasi altra
larghezza, ma non richiede la gaussianità come ipotesi.


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

## I plot in `images/`

**`plot_res_q68.png` / `.pdf`** — il plot principale, prodotto da
`plotting.py`. Pannello superiore: $\sigma_{68}(p_T)/p_T$ in funzione di
$p_T^{truth}$, log-log, un colore per bin di $|\eta|$ (le 6 curve della
legenda). I marker sono i dati (barra d'errore = il maggiore fra l'errore
statistico $\sigma_{68}/\sqrt{2N}$ e il floor sistematico 10%, vedi sopra), le
linee sono il fit a 3 termini

$$\frac{\sigma_{p_T}}{p_T} = \sqrt{\frac{r_0^2}{p_T^2} + r_1^2 + (r_2\, p_T)^2}$$

disegnate su **tutto** il range visibile, anche oltre gli 800 GeV di
`PT_FIT_MAX` dove il fit non è più vincolato dai dati (le curve lì sono
un'estrapolazione, non una misura). Il pannello inferiore mostra il residuo
relativo $(\text{data} - \text{fit})/\text{fit}$ punto per punto: piatto
intorno a zero fino a ~500-800 GeV, poi la curva estrapolata si stacca in
modo sistematico dai punti (fino a -50%) perché lì le code non gaussiane
fanno uscire $\sigma_{68}$ dalla forma a un solo parametro di scala che la
formula assume — vedi "Il fit funziona, ma solo fino a ~800 GeV" sopra per
la spiegazione completa.

**`plot_res_gaus.png` / `.pdf`** — identico a `plot_res_q68`, ma con lo
stimatore gaussiano (fit iterativo entro $\pm 2\sigma$ dal core, vedi
`resolution.py`) al posto di $\sigma_{68}$. Serve solo come confronto: la
differenza fra i parametri di questo fit e di quello nominale è la
sistematica sul metodo riportata nella tabella "Sistematiche".

**`plot_confronto_stimatori.png`** — sovrappone direttamente i due
stimatori punto per punto, **senza fit**: marker pieni = $\sigma_{68}$,
marker vuoti = $\sigma$ gaussiana, stesso colore per bin di $|\eta|$. A
basso $p_T$ i due stimatori coincidono (le distribuzioni sono quasi
gaussiane); salendo in $p_T$ i marker vuoti iniziano a scostarsi verso il
basso rispetto ai pieni — è la stessa sistematica di metodo vista sopra,
qui visibile a occhio senza passare dal fit.

**`table_res_q68.pdf`** — tabella riassuntiva generata da `report.py`: per
ogni bin di $|\eta|$, numero di punti entrati nel fit, $r_0$ del fit
libero, $\chi^2$/ndf sia per il fit con $r_0$ libero sia per quello con
$r_0$ fissato a 0, e $r_2$ (il termine dominante ad alto $p_T$, evidenziato
in blu perché è il numero da confrontare con le prestazioni note di
ATLAS). Righe con $\chi^2$/ndf > 3 sono evidenziate in rosso — qui nessuna,
grazie al floor del 10%.

**`inspect/histos_eta{N}_{lin,log}.png`** — griglia di istogrammi di
risoluzione (uno per bin di $p_T$) per il bin di $|\eta|$ numero N,
prodotta da `inspect_bins.py`: ogni pannello mostra l'istogramma con la
gaussiana del fit sovrapposta e tre linee verticali a $q_{16}$, mediana,
$q_{84}$. Utile per vedere a occhio *dove* la distribuzione smette di
essere gaussiana: quando il picco della curva gaussiana e le linee dei
quantili iniziano a divergere visibilmente. Versione in scala lineare e
log-y dello stesso bin. `inspect/log_inspect_eta{N}.txt` è il log numerico
corrispondente (entries, outflow, RMS, $\sigma$ gaussiana, $\sigma_{68}$,
rapporto $q_{68}/\text{gaus}$, asimmetria — un bin di $p_T$ per riga).

**`log_analisi.txt`** — log testuale completo di `analyze.py`: per ogni
bin di $|\eta|$, i sei tentativi di fit multistart (quale seed converge,
quale $\chi^2$/ndf, quale vince), i bin scartati e il motivo, la
correlazione $r_0$-$r_1$, e le sistematiche.

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

### Il fit funziona, ma solo fino a ~800 GeV

Sul range completo il fit non convergeva a niente di sensato: chi2/ndf da 81 a
83849 e residui fino al ±50%, con una forma sistematica (gobba positiva fra
100 e 800 GeV, poi sotto il fit sopra il TeV) — non rumore, un vero
disaccordo di forma. Due cause, non una:

1. Con decine di milioni di entries per bin l'errore statistico su
   $\sigma_{68}$ (sigma/sqrt(2N)) è così piccolo che anche uno scarto dello
   0.1% fa esplodere il chi2/ndf. Non è la formula che è sbagliata, sono gli
   errori che pretendono una precisione che nessuna parametrizzazione a 3
   parametri può avere.
2. Oltre qualche centinaio di GeV le code non gaussiane (vedi asimmetria e
   $q_{68}/\text{gaus}$ sopra) iniziano a mangiare nella finestra 16-84%:
   $\sigma_{68}$ smette di essere un parametro di scala pulito, quindi
   nessuna formula a 3 termini può descriverlo lì, giusta o sbagliata che sia.

Rimedio (in `config.py`/`fitting.py`): un floor sistematico sull'errore di
$\sigma_{68}$ prima del fit, e il **fit ristretto a $p_T < 800$ GeV**
(`PT_FIT_MAX`), tarato empiricamente come il punto oltre cui il chi2/ndf
peggiora in modo netto e monotono. I punti oltre 800 GeV restano nel grafico
(sono misure valide, vedi tabella sopra) ma non entrano nel fit; la curva è
comunque disegnata estrapolata su tutto il range per mostrare dove diverge.

Il floor non è arbitrario: con un floor relativo uniforme (`MIN_REL_ERR`) il
chi2/ndf scala esattamente come $1/\text{floor}^2$ — i parametri migliori del
fit non cambiano affatto, cambia solo quanto "gridiamo" il disaccordo residuo.
Quindi il floor giusto è quello che porta chi2/ndf $\approx 1$: non un numero
scelto per far tornare il fit, ma la **sistematica intrinseca misurata**
della parametrizzazione a 3 parametri. Viene **10%**.

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 36.3 | 0.0181 ± 0.0011 | 0.224 ± 0.012 | 0.58 |
| 0.1 - 1.05 | 0.000 ± 8.98 | 0.0201 ± 0.0010 | 0.126 ± 0.008 | 1.54 |
| 1.05 - 1.3 | 0.000 ± 37.2 | 0.0219 ± 0.0010 | 0.124 ± 0.009 | 0.51 |
| 1.3 - 1.7 | 0.000 ± 32.3 | 0.0305 ± 0.0014 | 0.161 ± 0.011 | 1.68 |
| 1.7 - 2.5 | 0.000 ± 32.5 | 0.0272 ± 0.0011 | 0.089 ± 0.008 | 0.64 |
| 2.5 - 2.8 | 0.223 ± 0.334 | 0.0293 ± 0.0019 | 0.104 ± 0.010 | 0.08 |

L'errore su $r_0$ è enorme rispetto a prima (era ±0.001-0.006, poi ±3-6 col
floor al 2%): non è un peggioramento, è che quella precisione era un
artefatto degli errori troppo piccoli. Con la sistematica vera $r_0$ è
semplicemente non vincolato ovunque — **anche nel bin 2.5-2.8**, dove con un
floor più stretto sembrava significativo (vedi sotto).

Sotto ~500-800 GeV il fit segue i dati in senso stretto (residui ~0, banda ±10%).
Sopra il TeV la curva estrapolata diverge dai punti (fino al -50%): è
atteso, è la regione dove le code non gaussiane dominano — vedi
`images/plot_res_q68.png`, pannello dei residui.

### Sistematiche

Nominale ($\sigma_{68}$, fit fino a 800 GeV) confrontato con due varianti:
$\sigma$ dal fit gaussiano (stesso range), e fit esteso fino a 2 TeV.

| $\|\eta\|$ | $r_2$ | stat | syst | syst % |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.2236 | 0.0116 | 0.0639 | 29% |
| 0.1 - 1.05 | 0.1257 | 0.0082 | 0.0271 | 22% |
| 1.05 - 1.3 | 0.1239 | 0.0085 | 0.0284 | 23% |
| 1.3 - 1.7 | 0.1606 | 0.0113 | 0.0515 | 32% |
| 1.7 - 2.5 | 0.0893 | 0.0083 | 0.0244 | 27% |
| 2.5 - 2.8 | 0.1041 | 0.0100 | 0.0180 | 17% |

Sistematica scesa dal 40-60% di prima al 17-32%: ancora non piccola (la
formula resta un'approssimazione), ma non più "il parametro non è definito".
La colonna "stat" ora include il floor del 10%, quindi non è più statistica
pura ma l'incertezza totale del fit — la vecchia "stat" (sigma/sqrt(2N)) era
sub-permille e non diceva niente di utile.

### $r_0$

Compatibile con zero **in tutti i bin, incluso 2.5-2.8** dove prima (con il
floor troppo stretto al 2%) sembrava significativo: $r_0 = 0.322 \pm 0.002$
sul range completo, poi $0.223 \pm 0.067$ col floor al 2%, ora $0.223 \pm
0.334$ col floor onesto al 10% — la stessa stima centrale, ma la
significatività era un artefatto di errori troppo piccoli, non un segnale
vero. Resta comunque coerente con l'assunzione $r_0 = 0$ altrove: il termine
di perdita di energia nel materiale conta solo a $p_T$ basso, e il punto più
basso è a 25 GeV.

### Regione oltre 800 GeV

Non è coperta dal fit: $\sigma_{68}$ misurato lì resta una misura valida
(vedi tabella "le misure sono solide" sopra), ma non gli si chiede di seguire
la formula a 3 termini: le code crescenti (asimmetria fino a +0.21,
$q_{68}/\text{gaus}$ fino a 1.71 in $|\eta|<0.1$) la rendono una regione a
parte, non descrivibile da un singolo parametro di scala.

Una spiegazione fisica plausibile: a bassa energia i muoni perdono energia
quasi solo per ionizzazione, che è ~costante (minimum ionizing particle) —
è il regime in cui vive il termine $r_0/p_T$. Oltre una certa energia
("energia critica" del muone nel materiale, che per materiali tipici
di un rivelatore è dell'ordine del centinaio di GeV fino al TeV) le perdite
radiative (bremsstrahlung, produzione di coppie, ecc...) iniziano ad aumentarre crescondo ~linearmente con l'energia, quindi con $p_T$. Sono
processi rari ma con perdite singole grandi: producono proprio la coda destra
asimmetrica (pT reco sottostimato) che cresce con $p_T$ e che si vede
nell'asimmetria e nel $q_{68}/\text{gaus}$. La soglia empirica di ~800 GeV
dove il fit smette di funzionare è nell'ordine di grandezza giusto per
questo effetto anche se non è una prova, ma è coerente.

