#!/bin/bash
#BSUB -J random_pheno_group[1-1000]
#BSUB -cwd _tmp/common_var_ids
#BSUB -oo random_pheno%I.%J.out
#BSUB -eo random_pheno%I.%J.error
#-#BSUB -u miltondp@gmail.com
#-#BSUB -N
#BSUB -n 1
#BSUB -R "rusage[mem=10GB]"
#BSUB -M 10GB
#BSUB -W 0:30

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
POST_GWAS_DIR="${PHENOPLIER_NULLSIM_RESULTS_DIR}/post_imputed_gwas"
OUTPUT_DIR="${PHENOPLIER_NULLSIM_RESULTS_DIR}/final_imputed_gwas"
mkdir -p ${OUTPUT_DIR}

# GWAS_JOBINDEX=`expr $LSB_JOBINDEX - 1`
# GWAS_JOBINDEX="0000"

GWAS_JOBINDEX=${pheno_id}

python ${CODE_DIR}/15_common_variant_ids.py \
  --input-gwas-file ${POST_GWAS_DIR}/random.pheno${GWAS_JOBINDEX}.glm-imputed.txt.gz \
  --common-variant-ids-file ${POST_GWAS_DIR}/common_variant_ids.pkl \
  --output-dir ${OUTPUT_DIR}

