poetry run python -m phenoplier run gene-corr cov \
-r GTEX_V8 \
-m MASHR

# one phenotype is selected
poetry run python -m phenoplier run gene-corr preprocess  \
-c phenomexcan_rapid_gwas \
-g /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gwas_parsing/full/22617_7112.txt.gz \
-s /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/spredixcan/rapid_gwas_project/22617_7112 \
-n 22617_7112-gtex_v8-{tissue}-2018_10.csv \
-f /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/smultixcan/rapid_gwas_project/smultixcan_22617_7112_ccn30.tsv.gz \
-r GTEX_V8 \
-m MASHR

# correlate
nohup bash -c 'parallel \
"poetry run python -m phenoplier run gene-corr correlate \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-m MASHR \
-w \
-s {}" ::: {1..22} \
> my_log_file.log 2>&1' &

poetry run python -m phenoplier run gene-corr correlate \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-m MASHR \
-w \
-s 1 \
-i "/tmp/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/" \
-o "/home/haoyu/"


poetry run python -m phenoplier run gene-corr correlate \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-m MASHR \
-s 1


# post
poetry run python -m phenoplier run gene-corr postprocess \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-m MASHR

# filter
poetry run python -m phenoplier run gene-corr filter \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-d 5 \
-m MASHR

# generate
nohup bash -c "parallel -k --lb --halt 1 -j10 \
    poetry run python -m phenoplier run gene-corr generate \
    -c phenomexcan_rapid_gwas \
    -r GTEX_V8 \
    -m MASHR \
    -e 0.01 \
    -l '{}' \
    ::: {1..117}" >> generate_output.log 2>&1 &

# rerun if time: 22 19 18 17 15 14 13 12 11 10 .. 2

nohup bash -c "parallel -k --lb -j10 \
    poetry run python -m phenoplier run gene-corr generate \
    -c phenomexcan_rapid_gwas \
    -r GTEX_V8 \
    -m MASHR \
    -e 0.01 \
    -l '{}' \
    ::: {30..40}" >> generate_output2.log 2>&1 &

poetry run python -m phenoplier run gene-corr generate \
-c phenomexcan_rapid_gwas \
-r GTEX_V8 \
-m MASHR \
-e 0.01 \
-l 1





# Dev notes
# Add model z file as a cli option
# check model z file LV names (or convert to LVs, not Vs)
# Parallelize lv-trait regression

# Cherrypick LV
45 12 14 68 115 1 3 43 76 56 99 28 65 34 37 5 84 35 72

3,24,36,37,76


# GLS
zcat "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/phenotypes_info.tsv.gz" | \
  tail -n +2 | \
  awk -F'\t' '$10 == "UK Biobank"' | \
  cut -f3 | \
  parallel -j10 run_job cluster_jobs/01-phenomexcan-rapid_gwas-sub_corr-template.sh {}


INPUT_SMULTIXCAN_DIR="/tmp/phenoplier/data/smultixcan/rapid_gwas"
OUTPUT_DIR="/tmp/phenoplier/results/gls/association"
GENE_CORR_FILE="/tmp/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv"

phenoplier run regression \
 -i ${INPUT_SMULTIXCAN_DIR}/smultixcan_${pheno_id}_ccn30.tsv.gz \
 -o ${OUTPUT_DIR}/gls_phenoplier-${pheno_id}.tsv.gz \
 -g ${GENE_CORR_FILE} \
 -c default \
 -m sub


bash ${CODE_DIR}/01_gls_phenoplier.sh \
  --input-file ${INPUT_SMULTIXCAN_DIR}/smultixcan_${pheno_id}_ccn30.tsv.gz \
  --gene-corr-file ${GENE_CORR_FILE} \
  --covars "gene_size gene_size_log gene_density gene_density_log" \
  --debug-use-sub-gene-corr 1 \
  --output-file ${OUTPUT_DIR}/gls_phenoplier-${pheno_id}.tsv.gz

#LV1, LV3, LV28, LV34, LV37, LV43, LV76
# 1, 3, 28, 34, 37, 43, 76

21001_raw, 23104_raw, E4_OBESITY, NAFLD, 20002_1223, E66, E4_OBESITYNAS, 21002_raw, 3160_raw

21001_raw-Body_mass_index_BMI 21001_raw
23104_raw-Body_mass_index_BMI 23104_raw
E4_OBESITY-Obesity E4_OBESITY
NAFLD-Nonalcoholic_fatty_liver_disease NAFLD
E4_DM2-Type_2_diabetes 20002_1223
21002_raw-Weight 21002_raw
3160_raw-Weight_manual_entry 3160_raw
E66-Diagnoses_main_ICD10_E66_Obesity E66
E4_OBESITYNAS-Obesity_otherunspecified E4_OBESITYNAS