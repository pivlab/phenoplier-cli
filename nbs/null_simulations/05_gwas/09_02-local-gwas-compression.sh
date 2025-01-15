#!/bin/bash
# Local GWAS Compression Script
#
# This script compresses GWAS results locally using parallel processing.
# It allows configuration of input/output paths, phenotype range, and number of jobs.
#
# Dependencies:
# - parallel command
# - utils.sh from common directory
#
# Example usage:
#   # Use default values
#   ./09_02-local-gwas-compression.sh
#
#   # Specify custom paths and range
#   ./09_02-local-gwas-compression.sh \
#     -i /path/to/input \
#     -o /path/to/output \
#     -s 0 -e 999 \
#     -j 16

source ../common/utils.sh

# Parse command line arguments
usage() {
    echo "Usage: $0 [-i INPUT_DIR] [-o OUTPUT_DIR] [-s START_PHENO] [-e END_PHENO] [-j N_JOBS]"
    echo
    echo "Options:"
    echo "  -i INPUT_DIR    Input directory path (default: /mnt/data/proj_data/nullsim/raw)"
    echo "  -o OUTPUT_DIR   Output directory path (default: /mnt/data/proj_data/nullsim/compressed)"
    echo "  -s START_PHENO  Starting phenotype ID (default: 0)"
    echo "  -e END_PHENO    Ending phenotype ID (default: 9)"
    echo "  -j N_JOBS       Number of parallel jobs (default: number of CPU cores)"
    echo
    echo "Example:"
    echo "  $0 -i /data/input -o /data/output -s 0 -e 999 -j 16"
    exit 1
}

# Default values
data_dpath="/mnt/data/proj_data/nullsim/raw"
output_dpath="/mnt/data/proj_data/nullsim/compressed"
start_pheno=0
end_pheno=9
N_JOBS=$(nproc --all)

# Parse options
while getopts "i:o:s:e:j:h" opt; do
    case $opt in
        i) data_dpath=$OPTARG ;;
        o) output_dpath=$OPTARG ;;
        s) start_pheno=$OPTARG ;;
        e) end_pheno=$OPTARG ;;
        j) N_JOBS=$OPTARG ;;
        h) usage ;;
        ?) usage ;;
    esac
done

# Validate input parameters
if ! [[ "$start_pheno" =~ ^[0-9]+$ ]] || ! [[ "$end_pheno" =~ ^[0-9]+$ ]] || ! [[ "$N_JOBS" =~ ^[0-9]+$ ]]; then
    echo "Error: Phenotype IDs and N_JOBS must be non-negative integers"
    usage
fi

if [ "$start_pheno" -gt "$end_pheno" ]; then
    echo "Error: Start phenotype ID must be less than or equal to end phenotype ID"
    usage
fi

if [ "$N_JOBS" -le 0 ]; then
    echo "Error: N_JOBS must be greater than 0"
    usage
fi

if [ ! -d "$data_dpath" ]; then
    echo "Error: Input directory does not exist: $data_dpath"
    usage
fi

# Create output directory if it doesn't exist
mkdir -p "$output_dpath"

echo "Running local GWAS compression with:"
echo "  Input directory:   $data_dpath"
echo "  Output directory:  $output_dpath"
echo "  Start phenotype:   $start_pheno"
echo "  End phenotype:     $end_pheno"
echo "  Number of jobs:    $N_JOBS"
echo

parallel -j${N_JOBS} compress_gwas {} ${output_dpath} "no-phenoid-padding" ::: ${data_dpath}/${start_pheno}-${end_pheno}/*.assoc.txt
