#!/bin/bash
source ../common/utils.sh

file="/mnt/data/proj_data/phenoplier-cli/ukb-nullsim/plink-v1.1.0/plink_gwas.plink2.pheno200.glm.linear.assoc.txt"
compress_gwas ${file}

# manual compress and download
# ssh user@remote_host "bash -s" < my_script.sh

parallel -j${N_JOBS} compress_gwas {} ~/output "add-phenoid-padding" ::: ${data_dpath}/${start_pheno}-${end_pheno}/*.assoc.txt

dx upload srd --path dst