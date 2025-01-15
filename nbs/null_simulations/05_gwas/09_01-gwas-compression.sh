#!/bin/bash

# This script is used to compress the GWAS results for the null simulations directly on the RAP server.
# Warning: This script is not stable and may fail due to the RAP server's resource limitation.
# Long queueing time can lead to execution failure.
# It is recommended to use the `09_02-local-gwas-compression.sh` script to compress the GWAS results locally.

source ../common/rap.sh

# Parse command line arguments
usage() {
    echo "Usage: $0 [-s START_PHENO] [-e END_PHENO]"
    echo
    echo "Options:"
    echo "  -s START_PHENO  Starting phenotype ID (default: 200)"
    echo "  -e END_PHENO    Ending phenotype ID (default: 399)"
    echo
    echo "Example:"
    echo "  $0 -s 0 -e 999     # Compress GWAS results for phenotypes 0-999"
    echo "  $0 -s 200 -e 399   # Compress GWAS results for phenotypes 200-399"
    exit 1
}

# Default values
start_pheno=200
end_pheno=399

# Parse options
while getopts "s:e:h" opt; do
    case $opt in
        s) start_pheno=$OPTARG ;;
        e) end_pheno=$OPTARG ;;
        h) usage ;;
        ?) usage ;;
    esac
done

# Validate input parameters
if ! [[ "$start_pheno" =~ ^[0-9]+$ ]] || ! [[ "$end_pheno" =~ ^[0-9]+$ ]]; then
    echo "Error: Both parameters must be non-negative integers"
    usage
fi

if [ "$start_pheno" -gt "$end_pheno" ]; then
    echo "Error: Start phenotype ID must be less than or equal to end phenotype ID"
    usage
fi

echo "Compressing GWAS results for:"
echo "  Start phenotype: $start_pheno"
echo "  End phenotype:   $end_pheno"
echo

# RAP job settings
N_JOBS=$(nproc --all)
instance_type="mem2_ssd1_v2_x32"
project_id="project-GY4ZFqQJZ09y0qZVF376p9Q6"
vm_name="Null Simulation GWAS Compression"

# Compression node settings
plink_version="plink-v1.1.0"
rap_dpath="${project_id}:/haoyu_test/phenoplier/null_sim/01-output/${plink_version}/${start_pheno}-${end_pheno}"
data_dpath="/home/dnanexus/plink-gwas"
rap_upload_dir="${project_id}:/haoyu_test/phenoplier/null_sim/02-compressed"

# Create the VM
dx_output=$(run_cloud_workstation "12h" "${vm_name}" "compression" ${instance_type})
job_name=$(echo "${dx_output}" | head -n 1)
echo "Creating RAP job: ${job_name}"
sleep 30  # Wait for the VM to be ready


str_install_parallel="
sleep 10 && \
if ! command -v parallel &> /dev/null; then
    sudo apt install parallel -y;
fi && \
"

str_download_from_rap="
data_dpath=${data_dpath} && \
mkdir -p ${data_dpath} && \
dx select --level=VIEW ${project_id} && \
dx download ${rap_dpath} -r -a -f -o ${data_dpath}
"

# Combine the two parts
command_string="${str_install_parallel}${str_download_from_rap}"

echo "$command_string"

dx ssh ${job_name} -t "${command_string}"
