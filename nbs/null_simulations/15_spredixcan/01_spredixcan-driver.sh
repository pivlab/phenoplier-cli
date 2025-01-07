# Iterate over all random phenotype ids, chromosomes and batch ids and submit a job for each combination.
# IMPORTANT: These are a lot of tasks. You might want to split jobs by chaning the range in first for line:
#   0..199
#   200..399
#   400..599
#   600..799
#   800..999

tissues=$(find "$PHENOPLIER_TWAS_PREDICTION_MODELS_MASHR" -name "*.db" | sed "s|$PHENOPLIER_TWAS_PREDICTION_MODELS_MASHR_PREFIX||"  | sed 's|\.db$||' | awk -F'/' '{print $NF}' | paste -sd ' ' -)

for pheno_id in {0..9}; do
  padded_pheno_id=$(printf "%04d" "$pheno_id")
  for tissue in $tissues; do
    export pheno_id=$padded_pheno_id tissue
    cat cluster_jobs/01_spredixcan_job-template.sh | envsubst '${pheno_id} ${tissue}' | bash
  done
done

