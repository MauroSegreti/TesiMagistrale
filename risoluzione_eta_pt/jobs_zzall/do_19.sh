#!/bin/bash
unset DISPLAY
echo "Running on host $(hostname)"
echo "Input file: /eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root/user.lucam.51077380._000020.ANALYSIS.root"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

export PYTHONPATH=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt:$PYTHONPATH

WORK=/eos/user/m/masegret/risoluzione_zzall_out/job_19
mkdir -p $WORK
cd $WORK

python3 /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_eta_pt/main_zzall.py /eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root/user.lucam.51077380._000020.ANALYSIS.root
echo "Exit code: $?"
