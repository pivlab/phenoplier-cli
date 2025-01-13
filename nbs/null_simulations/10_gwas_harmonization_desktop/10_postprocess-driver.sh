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
    padded_i=$i
    echo "Processing GWAS index: ${padded_i}"
    
    # Export the GWAS_JOBINDEX
    export GWAS_JOBINDEX="${padded_i}"
    
    # Run the original script
    bash cluster_jobs/10_postprocessing_job.sh
    
    # Optional: add a small delay between jobs if needed
    # sleep 1
done
