1. Compute Covariance
=====================

To compute the covariance for each chromosome of all variants present in prediction models, use the ``cov`` sub-command:

.. code-block:: bash

   phenoplier run gene-corr cov -h

    Usage: phenoplier run gene-corr cov [OPTIONS]

    Computes the covariance for each chromosome of all variants present in prediction models.

   ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ *  --reference-panel          -r      [1000G|GTEX_V8]      Reference panel such as 1000G or GTEX_V8           │
   │                                                            [default: None]                                    │
   │                                                            [required]                                         │
   │ *  --eqtl-model               -m      [MASHR|ELASTIC_NET]  Prediction models such as MASHR or ELASTIC_NET     │
   │                                                            [default: None]                                    │
   │                                                            [required]                                         │
   │    --covariance-matrix-dtype  -t      [float32|float64]    The numpy dtype used for the covariance matrix.    │
   │                                                            [default: float64]                                 │
   │    --project-dir              -p      PATH                 Project directory                                  │
   │                                                            [default:                                          │
   │                                                            /home/haoyu/_database/projs/phenoplier-cli]        │
   │    --help                     -h                           Show this message and exit.                        │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   phenoplier run gene-corr cov \
   -r GTEX_V8 \
   -m MASHR

For reference purposes, this functionality migrates code logic from 
`05-snps_into_chr_cov.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/07-compile_gwas_snps_and_twas_genes.ipynb>`_.
