4. Postprocess
==============

To read all gene correlations across all chromosomes and compute a single correlation matrix by assembling a big correlation matrix with all genes, use the ``postprocess`` sub-command:

.. code-block:: bash

   phenoplier run gene-corr postprocess -h

    Usage: phenoplier run gene-corr postprocess [OPTIONS]

    Reads all gene correlations across all chromosomes and computes a single correlation matrix by assembling a 
    big correlation matrix with all genes.

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
   │    --plot-output-dir  -o      PATH                                    Output directory for plots              │
   │                                                                       [default: None]                         │
   │    --project-dir      -p      PATH                                    Project directory                       │
   │                                                                       [default:                               │
   │                                                                       /home/haoyu/_database/projs/phenoplier… │
   │    --help             -h                                              Show this message and exit.             │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   phenoplier run gene-corr postprocess \
   -c phenomexcan_rapid_gwas \
   -r GTEX_V8 \
   -m MASHR 

Reference
---------

This functionality migrates code logic from 
`15-postprocess_gene_expr_correlations.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/15-postprocess_gene_expr_correlations.ipynb>`_.
