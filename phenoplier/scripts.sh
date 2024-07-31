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
