#!/bin/bash
# Genera un job per ogni file di input, combinando Z (locale, se scaricata)
# e i Z' (letti via XRootD dalle liste Rucio .root.txt).
#
# Uso:  ./gen_jobs.sh
# Poi:  condor_submit condorSub.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_combinata_out

# Liste Rucio (.root.txt) dei sample Z' ad allineamento perfetto.
# NB: qui ci sono 4 masse (500, 1000, 3000, 8000). La 5000 sta in
# samples_esclusi/ ed e' volutamente fuori; per includerla.
# MisAligned_MC/: e' il campione disallineato.
LISTS=/afs/cern.ch/user/m/masegret/samples

# Z standard gia' scaricata: sta su EOS
Z_LOCAL=/eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root

# quanti file per job: 1 = massimo parallelismo
FILES_PER_JOB=1

ALL=$ANADIR/all_files.txt
: > $ALL

if [ ! -d "$LISTS" ]; then
    echo "[ERROR] Cartella delle liste non trovata: $LISTS"
    exit 1
fi


if [ -d "$Z_LOCAL" ]; then
    ls -d $Z_LOCAL/*.root >> $ALL
    N_Z=$(ls -d $Z_LOCAL/*.root | wc -l)
    echo "[INFO] Z standard: $N_Z file locali"
    ZP_LISTS=$(ls $LISTS/*Zp_mm*.root.txt 2>/dev/null)
else
    echo "[INFO] Z standard: non scaricata, uso la lista Rucio"
    ZP_LISTS=$(ls $LISTS/*.root.txt 2>/dev/null)
fi

if [ -z "$ZP_LISTS" ]; then
    echo "[ERROR] Nessuna lista Z' trovata in $LISTS"
    echo "        Contenuto della cartella:"
    ls -1 $LISTS
    exit 1
fi

# --- Z' (e Z, se non scaricata): URL remoti dalle liste ---
for t in $ZP_LISTS; do
    n=$(grep -c '[^[:space:]]' "$t")
    echo "[INFO] $(basename $t): $n file"
    grep '[^[:space:]]' "$t" >> $ALL
done

N=$(wc -l < $ALL)
echo "[INFO] TOTALE $N file di input"
if [ "$N" -eq 0 ]; then
    echo "[ERROR] Nessun file trovato. Controlla \$SAMPLES."
    exit 1
fi

mkdir -p "$ANADIR/jobs" "$ANADIR/logs" $OUTDIR
rm -f "$ANADIR"/jobs/do_*.sh "$ANADIR"/jobs/list_*.txt

split -l $FILES_PER_JOB -d -a 4 --additional-suffix=.txt \
      $ALL "$ANADIR/jobs/list_"

i=0
for lst in "$ANADIR"/jobs/list_*.txt; do
    cat > "$ANADIR/jobs/do_$i.sh" <<EOF
#!/bin/bash
unset DISPLAY
echo "Running on host \$(hostname)"
echo "Lista: $lst"
cat $lst

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source \$ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

# il proxy VOMS viene trasferito da condor (x509userproxy nel .sub):
# serve per leggere i file remoti dei Z' via XRootD
echo "X509_USER_PROXY = \$X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=$ANADIR:\$PYTHONPATH

WORK=$OUTDIR/job_$i
mkdir -p \$WORK
cd \$WORK

python3 $ANADIR/fill.py $lst
echo "Exit code: \$?"
EOF
    chmod +x "$ANADIR/jobs/do_$i.sh"
    i=$((i+1))
done

echo "[INFO] generati $i job in $ANADIR/jobs/"
echo "[INFO] output in $OUTDIR"