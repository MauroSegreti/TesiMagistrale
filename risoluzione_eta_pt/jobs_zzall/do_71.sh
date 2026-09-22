#!/bin/bash
unset DISPLAY
echo "Running on host $(hostname)"
echo "Input file: /eos/user/m/masegret/dati_locali/user.mmarr.mc23_13p6TeV.801865.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth5000.MCP_TESTNTUP.mc23e_ANALYSIS.root/user.mmarr.49805122._000001.ANALYSIS.root"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

export PYTHONPATH=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt:$PYTHONPATH

WORK=/eos/user/m/masegret/risoluzione_zzall_out/job_71
mkdir -p $WORK
cd $WORK

python3 /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt/main_zzall.py /eos/user/m/masegret/dati_locali/user.mmarr.mc23_13p6TeV.801865.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth5000.MCP_TESTNTUP.mc23e_ANALYSIS.root/user.mmarr.49805122._000001.ANALYSIS.root
echo "Exit code: $?"
