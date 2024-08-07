#!/bin/bash

# Define the directories and file paths
INPUT_SMULTIXCAN_DIR="/tmp/phenoplier/data/smultixcan/rapid_gwas_gls"
OUTPUT_DIR="/tmp/phenoplier/results/gls/"
GENE_CORR_FILE="/tmp/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv"

# List of pheno_ids
pheno_ids=("21001_raw" "23104_raw" "E4_OBESITY" "NAFLD" "20002_1223" "E66" "E4_OBESITYNAS" "21002_raw" "3160_raw")
# pheno_ids=("21001_raw")

# Loop through each pheno_id and run the command
for pheno_id in "${pheno_ids[@]}"
do
    echo "Running phenoplier for pheno_id: $pheno_id"
    poetry run python -m phenoplier run regression \
        -i "${INPUT_SMULTIXCAN_DIR}/smultixcan_${pheno_id}_ccn30.tsv.gz" \
        -o "${OUTPUT_DIR}/gls_phenoplier-${pheno_id}.tsv.gz" \
        -g "${GENE_CORR_FILE}" \
        -c default \
        -m sub \
        -d "keep-first" \
        -f "/tmp/phenoplier/data/multiplier/marc_model_z.pkl" \
        -l "LV3 LV24 LV36 LV37 LV76"
done