#!/bin/bash
# BSUB -J random_pheno[1-1000]
# BSUB -cwd _tmp/smultixcan
# BSUB -oo random_pheno%I.%J.out
# BSUB -eo random_pheno%I.%J.error
# -#BSUB -u miltondp@gmail.com
# -#BSUB -N
# BSUB -n 1
# BSUB -R "rusage[mem=8GB]"
# BSUB -M 8GB
# BSUB -W 1:00

# make sure we use the number of CPUs specified
export n_jobs=16
export PHENOPLIER_N_JOBS=${n_jobs}
export NUMBA_NUM_THREADS=${n_jobs}
export MKL_NUM_THREADS=${n_jobs}
export OPEN_BLAS_NUM_THREADS=${n_jobs}
export NUMEXPR_NUM_THREADS=${n_jobs}
export OMP_NUM_THREADS=${n_jobs}

CODE_DIR=${PHENOPLIER_REPO_DIR}/nbs/null_simulations/15_spredixcan
FINAL_IMPUTED_GWAS_DIR="${PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_40PCS}/final_imputed_gwas"
SPREDIXCAN_DIR="${PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_40PCS}/twas/spredixcan"
OUTPUT_DIR="${PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_40PCS}/twas/smultixcan"

# GWAS_JOBINDEX=`expr ${LSB_JOBINDEX} - 1`
GWAS_JOBINDEX=${pheno_id}

# +
bash ${CODE_DIR}/05_smultixcan.sh \
  --input-gwas-file ${FINAL_IMPUTED_GWAS_DIR}/random.pheno${GWAS_JOBINDEX}.glm-imputed.txt.gz \
  --spredixcan-folder ${SPREDIXCAN_DIR} \
  --phenotype-name "random.pheno${GWAS_JOBINDEX}" \
  --output-dir ${OUTPUT_DIR}

