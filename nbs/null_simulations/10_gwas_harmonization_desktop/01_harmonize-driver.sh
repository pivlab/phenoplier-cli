#!/bin/bash

# Check if start and end indices are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <start_index> <end_index>"
    echo "Example: $0 0 999"
    exit 1
fi

start_index=$1
end_index=$2

# Loop through the range
for i in $(seq $start_index $end_index); do
    echo "Processing GWAS index: ${i}"
    
    # Export the GWAS_JOBINDEX
    export pheno_id="${i}"
    
    # Run the original script
    bash cluster_jobs/01_harmonization_job.sh
    
    # Optional: add a small delay between jobs if needed
    # sleep 1
done