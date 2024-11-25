#!/bin/bash
# Use this script if you plan to compress the GWAS results locally

source ../common/utils.sh

data_dpath="/mnt/data/proj_data/nullsim/raw"
output_dpath="/mnt/data/proj_data/nullsim/compressed"
start_pheno=0
end_pheno=9
N_JOBS=$(nproc --all)

parallel -j${N_JOBS} compress_gwas {} ${output_dpath} "add-phenoid-padding" ::: ${data_dpath}/${start_pheno}-${end_pheno}/*.assoc.txt
