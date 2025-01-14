#!/bin/bash
#BSUB -J random_pheno[1-1000]
#BSUB -cwd _tmp/harmonization
#BSUB -oo random_pheno%I.%J.out
#BSUB -eo random_pheno%I.%J.error
#-#BSUB -u miltondp@gmail.com
#-#BSUB -N
#BSUB -n 1
#BSUB -R "rusage[mem=8GB]"
#BSUB -M 8GB
#BSUB -W 0:15

# make sure we use the number of CPUs specified
export n_jobs=16
export PHENOPLIER_N_JOBS=${n_jobs}
export NUMBA_NUM_THREADS=${n_jobs}
export MKL_NUM_THREADS=${n_jobs}
export OPEN_BLAS_NUM_THREADS=${n_jobs}
export NUMEXPR_NUM_THREADS=${n_jobs}
export OMP_NUM_THREADS=${n_jobs}

# Determine the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
source ${PARENT_DIR}/00_config.sh

CODE_DIR=${PHENOPLIER_REPO_DIR}/nbs/null_simulations/10_gwas_harmonization_desktop
GWAS_DIR="${PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_50PCS}/gwas"
OUTPUT_DIR="${PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_50PCS}/harmonized_gwas"

# GWAS_JOBINDEX=`expr $LSB_JOBINDEX - 1`
# GWAS_JOBINDEX="0000"

bash ${CODE_DIR}/01_harmonize.sh \
  --input-gwas-file ${GWAS_DIR}/random.pheno${GWAS_JOBINDEX}.glm.linear.tsv.gz \
  --liftover-chain-file ${PHENOPLIER_GENERAL_LIFTOVER_HG19_TO_HG38} \
  --output-dir ${OUTPUT_DIR}
