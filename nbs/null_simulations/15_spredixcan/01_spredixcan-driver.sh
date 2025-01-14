# Check if start and end parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <start_pheno_id> <end_pheno_id>"
    echo "Example: $0 0 4"
    exit 1
fi

start_pheno=$1
end_pheno=$2

# Validate input parameters
if ! [[ "$start_pheno" =~ ^[0-9]+$ ]] || ! [[ "$end_pheno" =~ ^[0-9]+$ ]]; then
    echo "Error: Both parameters must be non-negative integers"
    exit 1
fi

if [ "$start_pheno" -gt "$end_pheno" ]; then
    echo "Error: Start phenotype ID must be less than or equal to end phenotype ID"
    exit 1
fi

tissues=$(find "$PHENOPLIER_TWAS_PREDICTION_MODELS_MASHR" -name "*.db" | sed "s|$PHENOPLIER_TWAS_PREDICTION_MODELS_MASHR_PREFIX||"  | sed 's|\.db$||' | awk -F'/' '{print $NF}' | paste -sd ' ' -)

for pheno_id in $(seq $start_pheno $end_pheno); do
  for tissue in $tissues; do
    export pheno_id tissue
    cat cluster_jobs/01_spredixcan_job-template.sh | envsubst '${pheno_id} ${tissue}' | bash
  done
done

