# Gene‐Gene Correlation

This pipeline aims for generating the gene-gene correlation matrix, which feeds the `--lv-model-file` option in [Gene-Trait Regression](https://github.com/pivlab/phenoplier-cli/wiki/Gene%E2%80%90Trait-Regression). You can use the following command to check the available commands:

```bash
phenoplier run gene-corr -h

 Usage: phenoplier run gene-corr [OPTIONS] COMMAND [ARGS]...

 Execute a specific Phenoplier pipeline for gene-gene correlation matrix generation.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help  -h        Show this message and exit.                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ cov           Computes the covariance for each chromosome of all variants present in prediction models.       │
│ preprocess    Compiles information about the GWAS and TWAS for a particular cohort. For example, the set of   │
│               GWAS variants, variance of predicted expression of genes, etc.                                  │
│ correlate     Computes predicted expression correlations between all genes in the MultiPLIER models.          │
│ postprocess   Reads all gene correlations across all chromosomes and computes a single correlation matrix by  │
│               assembling a big correlation matrix with all genes.                                             │
│ filter        Reads the correlation matrix generated and creates new matrices with different "within          │
│               distances" across genes. For example, it generates a new correlation matrix with only genes     │
│               within a distance of 10mb.                                                                      │
│ generate      Computes an LV-specific correlation matrix by using the top genes in that LV only.              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

### 1. Compute Covariance

To compute the covariance for each chromosome of all variants present in prediction models, use the `cov` sub-command:

```bash
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
```

Example command used when testing:

```bash
phenoplier run gene-corr cov \
-r GTEX_V8 \
-m MASHR
```

For reference purposes, this functionality migrates code logic from [05-snps\_into\_chr\_cov.ipynb](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/07-compile\_gwas\_snps\_and\_twas\_genes.ipynb).

### 2. Preprocess

To compile information about the GWAS and TWAS for a particular cohort. For example, the set of GWAS variants, variance of predicted expression of genes, etc, use the `preprocess` sub-command:

```bash
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
```

Example command used when testing:

```bash
phenoplier run gene-corr preprocess  \
-c 1000g_eur \
-g /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/final_imputed_gwas/random.pheno0.glm-imputed.txt.gz \
-s /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/twas/spredixcan \
-n random.pheno0-gtex_v8-mashr-{tissue}.csv \
-f /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/twas/smultixcan/random.pheno0-gtex_v8-mashr-smultixcan.txt \
-r GTEX_V8 \
-m MASHR
```

For reference purposes, this functionality migrates code logic from [07-compile\_gwas\_snps\_and\_twas\_genes.ipynb ](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/05-snps\_into\_chr\_cov.ipynb).

### 3. Correlation

To compute predicted expression correlations between all genes in the MultiPLIER models, use the `correlate` sub-command:

```bash
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
```

Example command used when testing:

```bash
phenoplier run gene-corr correlate \
-c 1000g_eur \
  -r GTEX_V8 \
-m MASHR \
-s 1
```

You can use GNU Parallel to perform computations on different chromosomes in parallel (future iterations will integrate parallelism into the software itself):

```bash
nohup parallel phenoplier run gene-corr correlate \
-c 1000g_eur \
-r GTEX_V8 \
-m MASHR \
-s ::: {1..22} > phenoplier_parallel_output.log 2>&1 &
```

For reference purposes, this functionality migrates code logic from [10-gene\_expr\_correlations.ipynb ](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/10-gene\_expr\_correlations.ipynb).

### 4. Postprocess

To read all gene correlations across all chromosomes and computes a single correlation matrix by assembling a big correlation matrix with all genes, use the `postprocess` sub-command:

```bash
phenoplier run gene-corr postprocess -h

 Usage: phenoplier run gene-corr postprocess [OPTIONS]

 Reads all gene correlations across all chromosomes and computes a single correlation matrix by assembling a big
 correlation matrix with all genes.

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
```

Example command used when testing:

```bash
nohup bash -c 'parallel \
"poetry run python -m phenoplier run gene-corr correlate \
-c 1000g_eur \
-r GTEX_V8 \
-m MASHR \
-s {}" ::: {1..22} \
> phenoplier_postprocess_output.log 2>&1' &
```

For reference purposes, this functionality migrates code logic from [15-postprocess\_gene\_expr\_correlations.ipynb](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/15-postprocess\_gene\_expr\_correlations.ipynb).

### 5. Create Within-distance Matrices

To read the correlation matrix generated and creates new matrices with different "within distances" across genes. For example, it generates a new correlation matrix with only genes within a distance of 10mb, use the `filter` sub-command:

```bash
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
```

Example command used when testing:

```bash
phenoplier run gene-corr filter \
-c 1000g_eur \
-r GTEX_V8 \
-m MASHR 
```

For reference purposes, this functionality migrates code logic from [16-create\_within\_distance\_matrices.ipynb](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/16-create\_within\_distance\_matrices.ipynb).

### 6. Generatec Correlation Matrices Per LV

To compute an LV-specific correlation matrix by using the top genes in that LV only, use the `generate` sub-command:

```bash
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
```

Example command used when testing:

```bash
nohup bash -c "parallel -k --lb --halt 2 -j10 \
    poetry run python -m phenoplier run gene-corr generate \
    -c 1000g_eur \
    -r GTEX_V8 \
    -m MASHR \
    -e 0.01 \
    -l '{}' \
    ::: {1..987}" > parallel_output.log 2>&1 &
```

For reference purposes, this functionality migrates code logic from [18-create\_corr\_mat\_per\_lv.ipynb](https://github.com/pivlab/phenoplier/blob/main/nbs/15\_gsa\_gls/18-create\_corr\_mat\_per\_lv.ipynb).
