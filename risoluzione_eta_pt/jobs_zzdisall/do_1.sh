#!/bin/bash
unset DISPLAY
echo "Running on host $(hostname)"
echo "Input file: root://grid-dc.t2.mpcdf.mpg.de:1094//atlasgroupdisk/perf-muons/rucio/user/lucam/3f/92/user.lucam.50435891._000002.ANALYSIS.root"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

echo "X509_USER_PROXY = $X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt:$PYTHONPATH

WORK=/eos/user/m/masegret/risoluzione_zzdisall_out/job_1
mkdir -p $WORK
cd $WORK

python3 /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt/main_zzdisall.py root://grid-dc.t2.mpcdf.mpg.de:1094//atlasgroupdisk/perf-muons/rucio/user/lucam/3f/92/user.lucam.50435891._000002.ANALYSIS.root
echo "Exit code: $?"
