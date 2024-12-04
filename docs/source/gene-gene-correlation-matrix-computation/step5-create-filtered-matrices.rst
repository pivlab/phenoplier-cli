5. Create Within-Distance Matrices
==================================

To read the correlation matrix generated and create new matrices with different "within distances" across genes, use the ``filter`` sub-command. For example, it generates a new correlation matrix with only genes within a distance of 10mb.

.. code-block:: bash

   phenoplier run gene-corr filter -h

    Usage: phenoplier run gene-corr filter [OPTIONS]

    Reads the correlation matrix generated and creates new matrices with different "within distances" across genes.
    For example, it generates a new correlation matrix with only genes within a distance of 10mb.

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
   │    --distances                FLOAT                                   List of distances to generate           │
   │                                                                       correlation matrices for                │
   │                                                                       [default: 10, 5, 2]                     │
   │    --project-dir      -p      PATH                                    Project directory                       │
   │                                                                       [default:                               │
   │                                                                       /home/haoyu/_database/projs/phenoplier… │
   │    --help             -h                                              Show this message and exit.             │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Example command used when testing:

.. code-block:: bash

   phenoplier run gene-corr filter \
   -c phenomexcan_rapid_gwas \
   -r GTEX_V8 \
   -d 5 \
   -m MASHR 

Reference
---------

This functionality migrates code logic from 
`16-create_within_distance_matrices.ipynb <https://github.com/pivlab/phenoplier/blob/main/nbs/15_gsa_gls/16-create_within_distance_matrices.ipynb>`_.
