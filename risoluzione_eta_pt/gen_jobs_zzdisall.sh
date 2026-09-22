#!/bin/bash
# Come gen_jobs_zzall.sh, ma per Z disallineato (26 file, MisAligned_MC,
# via XRootD) + Z' disallineato (5 masse, via XRootD). Ogni job gira
# main_zzall.py (griglia pT estesa a 3 TeV) su un solo file. Serve il
# proxy VOMS sui nodi condor (file remoti via XRootD), come per
# gen_jobs_eta_disaligned.sh.
#
# Uso:  ./gen_jobs_zzdisall.sh
# Poi:  condor_submit condorSub_zzdisall.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_zzdisall_out
MISALIGNED_MC=/afs/cern.ch/user/m/masegret/MisAligned_MC

FILELIST="$ANADIR/files_zzdisall.txt"
cat "$ANADIR/files_disaligned.txt" > "$FILELIST"
for dsid_txt in \
    "$MISALIGNED_MC"/user.lucam.mc23_13p6TeV.801862.*.root.txt \
    "$MISALIGNED_MC"/user.lucam.mc23_13p6TeV.801863.*.root.txt \
    "$MISALIGNED_MC"/user.lucam.mc23_13p6TeV.801864.*.root.txt \
    "$MISALIGNED_MC"/user.lucam.mc23_13p6TeV.801865.*.root.txt \
    "$MISALIGNED_MC"/user.lucam.mc23_13p6TeV.801866.*.root.txt ; do
    cat "$dsid_txt" >> "$FILELIST"
done

N=$(wc -l < "$FILELIST")
echo "[INFO] Analisi in: $ANADIR"
echo "[INFO] Output in:  $OUTDIR"
echo "[INFO] $N file trovati (Z disaligned + Z' disaligned) -> $N job"

mkdir -p "$ANADIR/jobs_zzdisall" "$ANADIR/logs_zzdisall" $OUTDIR
rm -f "$ANADIR"/jobs_zzdisall/do_*.sh

i=0
while read -r f; do
    cat > "$ANADIR/jobs_zzdisall/do_$i.sh" <<EOF
#!/bin/bash
unset DISPLAY
echo "Running on host \$(hostname)"
echo "Input file: $f"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source \$ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

echo "X509_USER_PROXY = \$X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=$ANADIR:\$PYTHONPATH

WORK=$OUTDIR/job_$i
mkdir -p \$WORK
cd \$WORK

python3 $ANADIR/main_zzdisall.py $f
echo "Exit code: \$?"
EOF
    chmod +x "$ANADIR/jobs_zzdisall/do_$i.sh"
    i=$((i+1))
done < "$FILELIST"

echo "[INFO] generati $i script in $ANADIR/jobs_zzdisall/"
