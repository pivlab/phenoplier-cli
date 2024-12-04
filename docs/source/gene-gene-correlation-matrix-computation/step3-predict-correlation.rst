3. Predict Correlation
=======================

To compute predicted expression correlations between all genes in the MultiPLIER models, use the ``correlate`` sub-command:

.. code-block:: bash

   phenoplier run gene-corr correlate -h

    Usage: phenoplier run gene-corr correlate [OPTIONS]

    Computes predicted expression correlations between all genes in the MultiPLIER models.

   ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ *  --cohort-name                    -c      [1000g_eur|phenomexcan_rapid_gw  Cohort name [default: None]      │
   │                                             as|phenomexcan_astle|phenomexca  [required]                       │
   │                                             n_other]                                                          │
   │ *  --reference-panel                -r      [1000G|GTEX_V8]                  Reference panel such as 1000G or │
   │                                                                              GTEX_V8                          │
   │                                                                              [default: None]                  │
   │                                                                              [required]                       │
   │ *  --eqtl-model                     -m      [MASHR|ELASTIC_NET]              Prediction models such as MASHR  │
   │                                                                              or ELASTIC_NET                   │
   │                                                                              [default: None]                  │
   │                                                                              [required]                       │
   │ *  --chromosome                     -s      INTEGER                          Chromosome number (1-22)         │
   │                                                                              [default: None]                  │
   │                                                                              [required]                       │
   │    --smultixcan-condition-number    -n      INTEGER                          S-MultiXcan condition number     │
   │                                                                              [default: 30]                    │
   │    --project-dir                    -p      PATH                             Project directory                │
   │                                                                              [default:                        │
   │                                                                              /home/haoyu/_database/projs/phe… │
   │    --compute-correlations-within-…  -w                                       Compute correlations within      │
   │                                                                              distance                         │
   │    --debug                          -d                                       Run with debug mode              │
   │    --help                           -h                                       Show this message and exit.      │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   phenoplier run gene-corr correlate \
   -c phenomexcan_rapid_gwas \
   -r GTEX_V8 \
   -m MASHR \
   -s 1

Parallelism with GNU Parallel
-----------------------------

You can use GNU Parallel to perform computations on different chromosomes in parallel. Future iterations will integrate parallelism into the software itself.

.. code-block:: bash

   nohup bash -c 'parallel \
   "phenoplier run gene-corr correlate \
   -c phenomexcan_rapid_gwas \
   -r GTEX_V8 \
   -m MASHR \
   -s {}" ::: {1..22} \
   > /dev/null 2>&1' &

Reference
---------

This functionality migrates code logic from 
`10-gene_expr_correlations.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/10-gene_expr_correlations.ipynb>`_.
