6. Generate Correlation Matrices Per LV
=======================================

To compute an LV-specific correlation matrix by using the top genes in that LV only, use the ``generate`` sub-command.

.. code-block:: bash

   phenoplier run gene-corr generate -h

    Usage: phenoplier run gene-corr generate [OPTIONS]

    Computes an LV-specific correlation matrix by using the top genes in that LV only.

   ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ *  --cohort-name      -c      [1000g_eur|phenomexcan_rapid_gwas|phen  Cohort name [default: None] [required]  │
   │                               omexcan_astle|phenomexcan_other]                                                │
   │ *  --reference-panel  -r      [1000G|GTEX_V8]                         Reference panel such as 1000G or        │
   │                                                                       GTEX_V8                                 │
   │                                                                       [default: None]                         │
   │                                                                       [required]                              │
   │ *  --eqtl-model       -m      [MASHR|ELASTIC_NET]                     Prediction models such as MASHR or      │
   │                                                                       ELASTIC_NET                             │
   │                                                                       [default: None]                         │
   │                                                                       [required]                              │
   │ *  --lv-code          -l      INTEGER RANGE [x>=1]                    The code of the latent variable (LV) to │
   │                                                                       compute the correlation matrix for      │
   │                                                                       [default: None]                         │
   │                                                                       [required]                              │
   │    --lv-percentile    -e      FLOAT RANGE [0.0<=x<=1.0]               A number from 0.0 to 1.0 indicating the │
   │                                                                       top percentile of the genes in the LV   │
   │                                                                       to keep                                 │
   │                                                                       [default: 0.05]                         │
   │    --project-dir      -p      PATH                                    Project directory                       │
   │                                                                       [default:                               │
   │                                                                       /home/haoyu/_database/projs/phenoplier… │
   │    --help             -h                                              Show this message and exit.             │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   nohup bash -c "parallel -k --lb --halt 2 -j10 \
       phenoplier run gene-corr generate \
       -c phenomexcan_rapid_gwas \
       -r GTEX_V8 \
       -m MASHR \
       -e 0.01 \
       -l '{}' \
       ::: {1..987}" > parallel_output.log 2>&1 &

Reference
---------

This functionality migrates code logic from 
`18-create_corr_mat_per_lv.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/18-create_corr_mat_per_lv.ipynb>`_.
