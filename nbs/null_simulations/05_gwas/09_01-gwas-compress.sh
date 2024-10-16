#!/bin/bash
# station_name="null-sim worker"
# input_dir="~/nullsim/input/"
# input_out="~/nullsim/compressed/"
# OUTDIR="project-Gq7G9JQJYYYByQzg1b8XJG8Q:/phenoplier/null_sim/02-compressed"
OUTDIR="~/output"
INDIR="/home/dnanexus/nullsim/input/0-199"
N_JOBS=$(nproc --all)
instance_type="mem1_ssd1_v2_x36"

source ../common/rap.sh

if ! command -v expect &> /dev/null
then
    echo "expect is not installed. Installing now..."
    sudo apt install expect
else
    echo "Starting..."
fi

output=$(run_cloud_workstation "12h" "null-sim" "compression" ${instance_type})
job_name=$(echo "${output}" | head -n 1)
echo ${job_name}
sleep 5
dx ssh ${job_name}

removecols() {
   FILE=$1
   awk -F'\t' 'BEGIN {OFS = FS} {print $1,$2,$3,$4,$6,$9,$10,$12}' ${FILE} | gzip > ${OUTDIR}/${FILE}.tsv.gz
}

export -f removecols
sudo apt install parallel -y
parallel -j${N_JOBS} removecols {} ::: ${INDIR}/*.glm.linear.assoc.txt

plink_gwas.plink2.pheno99.glm.linear.assoc.txt.tsv.gz

