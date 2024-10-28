#!/bin/bash
source ../common/rap.sh

# Data range
start_pheno=200
end_pheno=399

# RAP job settings
N_JOBS=$(nproc --all)
instance_type="mem2_ssd1_v2_x32"
# Todo: set this as envvar and load it
# project_id="project-Gq7G9JQJYYYByQzg1b8XJG8Q" #mine
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


# str_install_parallel="
# sleep 10 && \
# if ! command -v parallel &> /dev/null; then
#     sudo apt install parallel -y;
# fi && \
# "

# str_download_from_rap="
data_dpath=${data_dpath} && \
mkdir -p ${data_dpath} && \
dx select --level=VIEW ${project_id} && \
dx download ${rap_dpath} -r -a -f -o ${data_dpath}
"

# # Combine the two parts
# command_string="${str_install_parallel}${str_download_from_rap}"

# # echo "$command_string"

# dx ssh ${job_name} -t "${command_string}"
