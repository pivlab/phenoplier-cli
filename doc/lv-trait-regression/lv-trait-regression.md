# LV‐Trait Regression

This section shows how to use the GLS command. First, we can check the help message by running the following command:

```bash
phenoplier run regression -h

Usage: phenoplier run regression [OPTIONS]

 Run the Generalized Least Squares (GLS) model by default. Note that you need to run "phenoplier init" first to
 set up the environment.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input-file        -i      PATH                               File path to S-MultiXcan result file        │
│                                                                   (tab-separated and with at least columns    │
│                                                                   'gene' and 'pvalue').                       │
│                                                                   [default: None]                             │
│                                                                   [required]                                  │
│ *  --output-file       -o      PATH                               File path where results will be written to. │
│                                                                   [default: None]                             │
│                                                                   [required]                                  │
│    --project-dir       -p      TEXT                               Path to the project directory that contains │
│                                                                   initialized settings files and data. If not │
│                                                                   provided, will use the current shell        │
│                                                                   directory.                                  │
│                                                                   [default:                                   │
│                                                                   /home/haoyu/_database/projs/phenoplier-cli] │
│    --model                     [gls|ols]                          Choose which regression model to use. OLS   │
│                                                                   is usually used for debugging / comparisson │
│                                                                   purpose.                                    │
│                                                                   [default: gls]                              │
│    --gene-corr-file    -f      PATH                               Path to a gene correlations file or folder. │
│                                                                   It's is mandatory if running a GLS model,   │
│                                                                   and not necessary for OLS.                  │
│                                                                   [default: None]                             │
│    --gene-corr-mode    -m      [sub|full]                         Use an LV-specific submatrix of the gene    │
│                                                                   correlation matrix.                         │
│                                                                   [default: sub]                              │
│    --dup-genes-action          [keep-first|keep-last|remove-all]  Decide how to deal with duplicate gene      │
│                                                                   entries in the input file. Mandatory if     │
│                                                                   gene identifies are duplicated.             │
│                                                                   [default: keep-first]                       │
│    --covars            -c      TEXT                               List of covariates to use. Separate them by │
│                                                                   spaces. If provided with 'default', the     │
│                                                                   default covariates will be used. Available  │
│                                                                   covariates:[all gene_size gene_size_log     │
│                                                                   gene_density gene_density_log               │
│                                                                   gene_n_snps_used gene_n_snps_used_log       │
│                                                                   gene_n_snps_used_density                    │
│                                                                   gene_n_snps_used_density_log]. And the      │
│                                                                   default covariates are: [gene_size          │
│                                                                   gene_size_log gene_density                  │
│                                                                   gene_density_log].                          │
│                                                                   [default: None]                             │
│    --cohort-name       -n      TEXT                               Directory where cohort metadata files are   │
│                                                                   stored.                                     │
│                                                                   [default: None]                             │
│    --lv-list                   TEXT                               List of LV (gene modules) identifiers on    │
│                                                                   which an association will be computed. All  │
│                                                                   the rest not in the list are ignored.       │
│                                                                   [default: None]                             │
│    --lv-model-file             PATH                               A file containing the LV model. It has to   │
│                                                                   be in pickle format, with gene symbols in   │
│                                                                   rows and LVs in columns.                    │
│                                                                   [default: None]                             │
│    --batch-id                  INTEGER                            With --batch-n-splits, it allows to         │
│                                                                   distribute computation of each LV-trait     │
│                                                                   pair across a set of batches.               │
│                                                                   [default: None]                             │
│    --batch-n-splits            INTEGER                            With --batch-id, it allows to distribute    │
│                                                                   computation of each LV-trait pair across a  │
│                                                                   set of batches.                             │
│                                                                   [default: None]                             │
│    --help              -h                                         Show this message and exit.                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

It will give you brief information about the command and its arguments.

Now you can try it out by running the following sample command:

```bash
phenoplier run regression \
           -p <project_dir> \
           -i <path_to_the_input_file> \
           -o <path_to_the_output_file> \
           --gene-corr-file <path_to_your_gene_corr_file> \
           --covars default (or other available options)
```

An example command used in our testing is:

```bash
phenoplier run regression \
 -i /home/haoyu/_database/projs/phenoplier-cli/test/data/gls/covars_test/random.pheno0-gtex_v8-mashr-smultixcan.txt \
 -o /tmp/phenoplier_test_output/test_main_run_regression/without_covars_random.pheno0.tsv \
 --gene-corr-file /home/haoyu/_database/projs/phenoplier-cli/test/data/gls/covars_test/gene_corr_file/gene_corrs-symbols-within_distance_5mb.per_lv \
 --covars default
```

Please adjust the option arguments according to your own data and file paths.
