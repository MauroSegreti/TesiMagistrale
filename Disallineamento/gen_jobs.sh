#!/bin/bash
# Genera un job per ogni file di input, letto via XRootD dalle liste Rucio.
#
# Nessun file viene scaricato: le liste .root.txt contengono URL root:// e i
# job leggono da remoto. Vedi Allineamento/gen_jobs.sh per il
# perche' (stesso identico script, solo campione diverso).
#
# Uso:  ./gen_jobs.sh
# Poi:  condor_submit condorSub.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_misaligned_out

# Liste dei sample MS-misaligned (tag mc23e_MSmisalign): Z (601190) + 5
# masse di Z' ZeroWidth (801862-801866). NON usare PerfectAlignment/ ne'
# Nominal_MC/: sono altre condizioni.
LISTS=/afs/cern.ch/user/m/masegret/MisAligned_MC

# quanti file per job: 1 = massimo parallelismo
FILES_PER_JOB=1

if [ ! -d "$LISTS" ]; then
    echo "[ERROR] Cartella delle liste non trovata: $LISTS"
    exit 1
fi

ALL=$ANADIR/all_files.txt
: > $ALL

FOUND=0
for t in $LISTS/*.root.txt; do
    [ -e "$t" ] || continue
    n=$(grep -c '[^[:space:]]' "$t")
    echo "[INFO] $(basename $t): $n file"
    grep '[^[:space:]]' "$t" >> $ALL
    FOUND=$((FOUND+1))
done

if [ "$FOUND" -eq 0 ]; then
    echo "[ERROR] Nessuna lista .root.txt in $LISTS"
    exit 1
fi

N=$(wc -l < $ALL)
echo "[INFO] $FOUND sample, TOTALE $N file di input"

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

# proxy VOMS trasferito da condor (x509userproxy nel .sub): serve per
# leggere i file via XRootD
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
