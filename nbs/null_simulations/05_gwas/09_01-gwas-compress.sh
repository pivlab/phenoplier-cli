#!/bin/bash
source ../common/rap.sh


# RAP job settings
N_JOBS=$(nproc --all)
instance_type="mem1_ssd1_v2_x36"
# Todo: set this as envvar and load it
project_id="project-Gq7G9JQJYYYByQzg1b8XJG8Q"
vm_name="Null Simulation GWAS Compression"

# Compression node settings
plink_version="plink-v1.1.0"
rap_dpath="${project_id}:/phenoplier/null_sim/01-output/${plink_version}"
data_dpath="/home/dnanexus/plink-gwas"

# # Create the VM
# dx_output=$(run_cloud_workstation "12h" "${vm_name}" "compression" ${instance_type})
# job_name=$(echo "${dx_output}" | head -n 1)
# echo "Creating RAP job: ${job_name}"
# sleep 30  # Wait for the VM to be ready


job_name="job-GvG5QzjJYYYJ8JPXk4ffXJ9j"

str_install_parallel="
sleep 5 && \
if ! command -v parallel &> /dev/null; then
    sudo apt install parallel -y;
fi && \
"

str_download_from_rap="
data_dpath=${data_dpath} && \
mkdir -p ${data_dpath} && \
dx select --level=VIEW ${project_id} && \
dx download ${rap_dpath} -r -a -o ${data_dpath}
"

# Combine the two parts
command_string="${str_install_parallel}${str_download_from_rap}"

# echo "$command_string"

dx ssh ${job_name} -t "${command_string}"
