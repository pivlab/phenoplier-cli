# This scirpt initilizes the environment for each cluster job

# Turn on dev mode for phenoplier
export ENV_FOR_DYNACONF="dev"
# Use Alpine's scratch directory for all compute jobs
# Caution: files are automatically removed 90 days after their initial creation in this directory.
export PHENOPLIER_ROOT_DIR="/scratch/alpine/${USER}/phenoplier"
export PHENOPLIER_GWAS_IMPUTATION_BASE_DIR="${PHENOPLIER_ROOT_DIR}/summary_gwas_imputation/"

