# Risoluzione in $p_T$ dei muoni — campioni MS-misaligned

Stessa identica misura di [`Allineamento`](../Allineamento/) —
stesso binning, stesso stimatore ($\sigma_{68}$), stesso fit a 3 termini,
stesso codice — ma sui campioni con **geometria disallineata** (tag
`mc23e_MSmisalign`) invece di `PerfectAlignment`. Per i dettagli su metodo,
formula, e come si legge il fit, vedi il README di `Allineamento`:
qui non li ripeto.

## Campioni (tag `mc23e_MSmisalign`, prodotti da `user.lucam`)

| DSID | campione |
|---|---|
| 601190 | Z → μμ (Powheg+Pythia8 AZNLO) |
| 801862 | Z′ ZeroWidth 500 GeV |
| 801863 | Z′ ZeroWidth 1000 GeV |
| 801864 | Z′ ZeroWidth 3000 GeV |
| 801865 | Z′ ZeroWidth 5000 GeV |
| 801866 | Z′ ZeroWidth 8000 GeV |

Stessi sei DSID di `Allineamento`, tag diverso.

## Preparare le liste

Stesso schema di `PerfectAlignment`: una lista `.root.txt` per DSID, con URL
`root://`, in `/afs/cern.ch/user/m/masegret/MisAligned_MC`. Nessun download:
`gen_jobs.sh` legge questi file via XRootD.

```bash
setupATLAS
lsetup rucio
voms-proxy-init -voms atlas

mkdir -p /afs/cern.ch/user/m/masegret/MisAligned_MC
cd /afs/cern.ch/user/m/masegret/MisAligned_MC

rucio list-dids --short 'user.lucam:user.lucam.mc23_13p6TeV.*.MCP_TESTNTUP.mc23e_MSmisalign_ANALYSIS.root' \
  | sed 's/^user.lucam://' | grep . > /tmp/dids.txt
while read NAME; do
  rucio list-file-replicas --protocols root --pfns "user.lucam:${NAME}" \
    | grep -o 'root://[^ ]*' | sort -u > "${NAME}.root.txt"
  echo "$NAME -> $(wc -l < "${NAME}.root.txt") file"
done < /tmp/dids.txt
```

Controlla che vengano fuori sei file `.txt`, uno per DSID della tabella sopra.

## Come giro

```bash
setupATLAS
voms-proxy-init -voms atlas --valid 24:00
cp /tmp/x509up_u$(id -u) $HOME/x509up
chmod 600 $HOME/x509up
export X509_USER_PROXY=$HOME/x509up

./gen_jobs.sh
condor_submit condorSub.sub
```

Analisi:

```bash
python3 analyze.py /eos/user/m/masegret/risoluzione_misaligned_out
python3 inspect_bins.py merged_res.root
python3 compare_alignment.py   # confronto diretto col nominale
python3 closure_test.py        # closure test su r0/r1/r2, vedi sotto
```

## Prima del primo giro vero

`EXPECTED_R2` in `config.py` è già alzato rispetto al nominale (il
disallineamento peggiora $r_2$, è il termine sensibile all'allineamento) ma è
una stima: se `print_window_summary()` o troppi bin scartati per outflow lo
smentiscono, alzalo ancora — dimensiona solo la finestra, non entra nel
risultato.

`PT_FIT_MAX` e `MIN_REL_ERR` sono ereditati dal nominale come punto di
partenza, ma sono stati calibrati là sui dati di `PerfectAlignment`: vanno
ricontrollati qui allo stesso modo (vedi il README di `Allineamento`
per il procedimento — in breve, il floor giusto è quello che porta
chi2/ndf ≈ 1, non un numero scelto a caso).

## Risultati

Primo giro: 31 job sottomessi (26 Zmumu + 5 Z′, tutti `user.lucam`), 30
completati — `job_24` (un file Zmumu su MPCDF) è andato in errore per un
redirect XRootD, non un problema della misura. Nessun bin scartato per
outflow con l'`EXPECTED_R2` alzato.

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

## I plot in `images/`

`plot_res_q68.png`/`.pdf`, `plot_res_gaus.png`/`.pdf`,
`plot_confronto_stimatori.png`, `table_res_q68.pdf` e `log_analisi.txt`
sono **gli stessi plot di [`Allineamento`](../Allineamento/)**, prodotti
dallo stesso codice (`plotting.py`, `report.py`), ma sui dati misaligned —
vedi la sezione "I plot in `images/`" del README di `Allineamento` per la
spiegazione di ciascuno, non la ripeto qui. Sotto solo i due plot nuovi di
questa cartella, quelli che confrontano i due campioni.

**`plot_confronto_allineamento.png` / `.pdf`** — generato da
`compare_alignment.py`. Pannello superiore: le curve nominale (marker
pieni, linea continua) e misaligned (marker vuoti, linea tratteggiata)
sovrapposte nello stesso grafico $\sigma_{68}(p_T)/p_T$ vs $p_T^{truth}$,
stesso colore per bin di $|\eta|$, entrambe fittate con la stessa formula
a 3 termini

$$\frac{\sigma_{p_T}}{p_T} = \sqrt{\frac{r_0^2}{p_T^2} + r_1^2 + (r_2\, p_T)^2}$$

Il pannello inferiore **non è un residuo** ma il rapporto continuo fra le
due curve di fit, misaligned/nominale, valutato su tutta l'intersezione
dei due range validi:

$$\frac{\sigma_{68}^{mis}(p_T)}{\sigma_{68}^{nom}(p_T)} = \frac{f^{mis}(p_T)}{f^{nom}(p_T)}$$

dove $f^{nom}$ e $f^{mis}$ sono le due curve di fit, cioè la formula a 3
termini qui sopra valutata con i parametri $r_0, r_1, r_2$ trovati dal fit
nominale e da quello misaligned rispettivamente — non i punti dati, la
curva continua.

A basso $p_T$ il rapporto è vicino a 1 (lì dominano $r_0$ e $r_1$, che il
disallineamento non tocca — vedi closure test sotto); sale con $p_T$
perché il termine che risente della geometria è $r_2\, p_T$, che cresce
linearmente; e si stabilizza al plateau asintotico $r_2^{mis}/r_2^{nom}$
per ogni bin di $|\eta|$ quando $r_2\, p_T$ arriva a dominare sugli altri
due termini — sono gli stessi numeri della tabella "Confronto diretto con
il nominale" qui sopra. Il plateau più alto (~4×) è per $2.5 \le |\eta| <
2.8$, il più basso (~1.4×) per $0.1 \le |\eta| < 1.05$: la curva teal (in
alto a destra nel pannello superiore) si stacca visibilmente prima e più
in alto delle altre.

**`table_closure_test.pdf`** — generata da `closure_test.py`: per ogni bin
di $|\eta|$, i tre parametri del fit libero — nominale, misaligned,
differenza in $N\sigma$ — affiancati per $r_0$, $r_1$, $r_2$. Le celle di
$r_0$/$r_1$ con $N\sigma > 2$ sarebbero evidenziate in rosso (qui nessuna
lo è): il test si aspetta che $r_0$ (perdita di energia nel materiale) e
$r_1$ (multiple scattering) restino compatibili fra i due campioni, perché
nessuno dei due dipende da dove il software crede che siano le camere del
muon spectrometer, mentre $r_2$ — l'unico termine sensibile alla geometria
— si sposta. Vedi "Closure test dei fit" sotto per i numeri completi e
l'interpretazione fisica.

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
`images/plot_confronto_allineamento.png` per la curva completa e
`compare_alignment.py` per come è fatto)

**La degradazione da disallineamento cresce con $|\eta|$**: da ~1.4× nel
barrel centrale a ~4× nel forward (2.5-2.8). È fisicamente sensato: oltre
$|\eta| = 2.5$ le tracce sono standalone nel muon spectrometer (niente inner
detector, vedi i tre termini nel README di `Allineamento`), quindi
meno misure ridondanti per compensare l'errore di posizione delle camere
disallineate. Il barrel centrale, dove $r_2$ è già il più piccolo dei due
casi, è anche il più protetto dal disallineamento in termini relativi.

### Closure test dei fit

Il confronto sopra si basa solo su $r_2$, ma da solo non basta a escludere che
stia confrontando due fit fatti in modo diverso invece di due geometrie
diverse. Test più stringente: controllare anche $r_0$ ed $r_1$, che *non*
dovrebbero dipendere dalla geometria del muon spectrometer — $r_0$ è perdita
di energia nel materiale, $r_1$ è multiple scattering, entrambi indifferenti
a dove il software crede che siano le camere. Se il fit li vede spostarsi in
modo significativo fra nominale e misaligned, vuol dire che c'è qualcosa che
non va nel confronto (binning diverso, fit degenere, bug), non un vero
effetto fisico.

`closure_test.py` fa esattamente questo: per ogni bin di $|\eta|$ prende i
tre parametri del fit libero (stesso `fit` usato ovunque, non
`fit_fixed0`) da entrambi i campioni e calcola la differenza in unità di
sigma combinata:

$$\sigma_{\text{comb}} = \sqrt{\sigma_{\text{nom}}^2 + \sigma_{\text{mis}}^2}
\qquad
N\sigma = \frac{|r_{\text{mis}} - r_{\text{nom}}|}{\sigma_{\text{comb}}}$$

È la propagazione standard sotto l'ipotesi che i due fit siano scorrelati —
ragionevole: sono due fit fatti su due sample statisticamente indipendenti
(campioni diversi, nessun evento in comune), quindi i loro errori si sommano
in quadratura. $N\sigma$ è un pull/z-score classico: quante sigma separano i
due valori, tenendo conto di entrambi gli errori insieme. Le celle con
$N\sigma > 2$ su $r_0$ o $r_1$ vengono segnalate in rosso nella tabella
(`images/table_closure_test.pdf`) — vorrebbe dire closure test fallito in
quella regione.

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
vincolato dal fit, vedi sopra — ma $r_1$ è ben misurato e torna comunque
entro 0.67 sigma ovunque). $r_2$ invece si sposta fra 4.6 e 12.6 sigma in
ogni bin: esattamente il comportamento atteso, essendo l'unico termine
sensibile alla geometria delle camere. Il fatto che sia l'unico a muoversi,
sempre nella stessa direzione (peggiora, mai migliora) e in modo crescente
con $|\eta|$ come il rapporto qui sopra, è la controprova che l'effetto è
reale e non un artefatto del fit.

### $r_2$ residuo: quanto ci mette il disallineamento da solo

Il confronto e il closure test sopra dicono *che* $r_2$ peggiora e *che* è
l'unico a farlo, ma non isolano un numero per "quanto smearing aggiunge il
disallineamento da solo", separato dalla risoluzione intrinseca che c'è
già con la geometria perfetta. Per farlo serve un'ipotesi in più:
$r_2$ è un termine di risoluzione (pesa come $r_2 \times p_T$ nella formula
a 3 termini), e sorgenti di smearing **indipendenti** si sommano in
quadratura, non linearmente. Se il disallineamento aggiunge uno smearing
extra e scorrelato rispetto a quello già presente nel campione nominale,
allora

$$\left(r_2^{\text{misaligned}}\right)^2 = \left(r_2^{\text{nominale}}\right)^2 + \left(r_2^{\text{residual}}\right)^2
\quad\Longrightarrow\quad
r_2^{\text{residual}} = \sqrt{\left(r_2^{\text{misaligned}}\right)^2 - \left(r_2^{\text{nominale}}\right)^2}$$

con l'errore propagato dalla stessa forma:

$$\sigma_{\text{residual}} = \sqrt{\left(\frac{r_2^{\text{mis}}}{r_2^{\text{res}}} \times \sigma_{\text{mis}}\right)^2 + \left(\frac{r_2^{\text{nom}}}{r_2^{\text{res}}} \times \sigma_{\text{nom}}\right)^2}$$

è la solita propagazione degli errori (regola della catena su
$f = \sqrt{a^2-b^2}$: $\partial f/\partial a = a/f$, $\partial f/\partial b
= -b/f$, poi si sommano in quadratura i due termini pesati per gli errori
su $a$ e $b$), dove $\sigma_{\text{nom}}$, $\sigma_{\text{mis}}$ sono gli stessi errori
stat+syst in quadratura della tabella "Confronto diretto" sopra (statistica
del fit più sistematica su metodo e range, vedi
`Allineamento/README.md`, "Sistematiche"). È la stessa logica di
`closure_test.py`, calcolata da `residual_r2.py`:

```bash
python3 residual_r2.py
```

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
misaligned/nominale è più alto (vedi tabella sopra). Nel barrel centrale
($0.1 \le |\eta| < 1.05$) resta comunque maggioritario (76%) ma con errore
relativo più grande (~30%), perché lì $r_2^{\text{nom}}$ e
$r_2^{\text{mis}}$ sono più vicini fra loro e la sottrazione in quadratura
amplifica l'errore relativo — è la stessa ragione per cui $\sigma_f$ va
come $r_2^{\text{mis}}/r_2^{\text{res}}$ nella formula sopra: più $r_2^{\text{res}}$
è piccolo rispetto a $r_2^{\text{mis}}$, più l'errore si gonfia.

L'ipotesi di indipendenza è la stessa che sta dietro il closure test: se
$r_0$ ed $r_1$ non si fossero spostati nella verifica sopra (e non si
spostano), è plausibile che anche gli altri contributi allo smearing —
perdita di energia nel materiale, multiple scattering — restino invariati
e scorrelati dal termine di allineamento, che è esattamente l'assunzione
che rende valida la somma in quadratura qui.
