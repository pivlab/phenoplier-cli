# This scirpt initilizes the environment for each cluster job

# Use Alpine's scratch directory for all compute jobs
# Caution: files are automatically removed 90 days after their initial creation in this directory.
# export PHENOPLIER_ROOT_DIR="/scratch/alpine/${USER}/phenoplier"
export PHENOPLIER_GWAS_IMPUTATION_BASE_DIR="${PHENOPLIER_ROOT_DIR}/summary_gwas_imputation/"
export PHENOPLIER_NULLSIM_RESULTS_DIR=$PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_50PCS


