2. Preprocess
=============

To compile information about the GWAS and TWAS for a particular cohort, such as the set of GWAS variants or the variance of predicted expression of genes, use the ``preprocess`` sub-command:

.. code-block:: bash

   phenoplier run gene-corr preprocess -h

    Usage: phenoplier run gene-corr preprocess [OPTIONS]

    Compiles information about the GWAS and TWAS for a particular cohort. For example, the set of GWAS variants,
    variance of predicted expression of genes, etc.

   ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ *  --cohort-name              -c      [1000g_eur|phenomexcan_rapid_gwas|  Cohort name [default: None]         │
   │                                       phenomexcan_astle|phenomexcan_othe  [required]                          │
   │                                       r]                                                                      │
   │ *  --gwas-file                -g      PATH                                GWAS file  [default: None]          │
   │                                                                           [required]                          │
   │ *  --spredixcan-folder        -s      PATH                                S-PrediXcan folder [default: None]  │
   │                                                                           [required]                          │
   │ *  --spredixcan-file-pattern  -n      TEXT                                S-PrediXcan file pattern            │
   │                                                                           [default: None]                     │
   │                                                                           [required]                          │
   │ *  --smultixcan-file          -f      PATH                                S-MultiXcan file [default: None]    │
   │                                                                           [required]                          │
   │ *  --reference-panel          -r      [1000G|GTEX_V8]                     Reference panel such as 1000G or    │
   │                                                                           GTEX_V8                             │
   │                                                                           [default: None]                     │
   │                                                                           [required]                          │
   │ *  --eqtl-model               -m      [MASHR|ELASTIC_NET]                 Prediction models such as MASHR or  │
   │                                                                           ELASTIC_NET                         │
   │                                                                           [default: None]                     │
   │                                                                           [required]                          │
   │    --project-dir              -p      PATH                                Project directory                   │
   │                                                                           [default:                           │
   │                                                                           /home/haoyu/_database/projs/phenop… │
   │    --help                     -h                                          Show this message and exit.         │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   phenoplier run gene-corr preprocess  \
   -c phenomexcan_rapid_gwas \
   -g /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gwas_parsing/full/22617_7112.txt.gz \
   -s /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/spredixcan/rapid_gwas_project/22617_7112 \
   -n 22617_7112-gtex_v8-{tissue}-2018_10.csv \
   -f /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/smultixcan/rapid_gwas_project/smultixcan_22617_7112_ccn30.tsv.gz \
   -r GTEX_V8 \
   -m MASHR

For reference purposes, this functionality migrates code logic from 
`07-compile_gwas_snps_and_twas_genes.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/05-snps_into_chr_cov.ipynb>`_.
