for pheno_id in {0..0}; do
  # Pad pheno_id to 4 digits
  padded_pheno_id=$(printf "%04d" "$pheno_id")
  for chromosome in {1..1}; do
    for batch_id in {0..0}; do
      export pheno_id=$padded_pheno_id chromosome batch_id
      cat cluster_jobs/05_imputation_job-template.sh | envsubst '${pheno_id} ${chromosome} ${batch_id}' | bash
    done
  done
done