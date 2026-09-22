#!/bin/bash
# Come gen_jobs_eta.sh, ma per il campione Z disallineato (MisAligned_MC,
# 26 file letti via XRootD remoto -- serve il proxy VOMS sui nodi condor).
#
# Uso:  ./gen_jobs_eta_disaligned.sh
# Poi:  voms-proxy-init -voms atlas --valid 24:00   (se serve rinnovarlo)
#       export X509_USER_PROXY=/tmp/x509up_u$(id -u)
#       condor_submit condorSub_disaligned.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_eta_disaligned_out
FILELIST=/afs/cern.ch/user/m/masegret/MisAligned_MC/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_MSmisalign_ANALYSIS.root.txt

echo "[INFO] Analisi in: $ANADIR"
echo "[INFO] Output in:  $OUTDIR"

cp "$FILELIST" "$ANADIR/files_disaligned.txt"
N=$(wc -l < "$ANADIR/files_disaligned.txt")
echo "[INFO] $N file trovati -> $N job"

mkdir -p "$ANADIR/jobs_disaligned" "$ANADIR/logs_disaligned" $OUTDIR
rm -f "$ANADIR"/jobs_disaligned/do_*.sh

i=0
while read -r f; do
    cat > "$ANADIR/jobs_disaligned/do_$i.sh" <<EOF
#!/bin/bash
unset DISPLAY
echo "Running on host \$(hostname)"
echo "Input file: $f"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source \$ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

# proxy VOMS trasferito da condor (x509userproxy nel .sub): serve per
# leggere il file remoto via XRootD
echo "X509_USER_PROXY = \$X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=$ANADIR:\$PYTHONPATH

WORK=$OUTDIR/job_$i
mkdir -p \$WORK
cd \$WORK

python3 $ANADIR/main.py $f
echo "Exit code: \$?"
EOF
    chmod +x "$ANADIR/jobs_disaligned/do_$i.sh"
    i=$((i+1))
done < "$ANADIR/files_disaligned.txt"

echo "[INFO] generati $i script in $ANADIR/jobs_disaligned/"
