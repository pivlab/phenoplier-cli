# Test command

poetry run python -m phenoplier run gls \
        -i /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/null_sims/twas/smultixcan/random.pheno17-gtex_v8-mashr-smultixcan.txt \
        --gene-corr-file /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/cohorts/1000g_eur/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv/ \
        --covars "gene_size gene_size_log gene_density gene_density_log" \
        --debug-use-sub-gene-corr 1 \
        -o /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/null_sims/phenoplier/1000g_eur/covars/gls-gtex_v8_mashr-sub_corr/test.tsv.gz