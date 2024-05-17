from types import MappingProxyType as ImmutableDict

RUN_GLS = ImmutableDict(
    {
        "input_file": "File path to S-MultiXcan result file (tab-separated and with at least columns 'gene' and 'pvalue')",
        "output_file": "File path where results will be written to",
        "gene_corr_file": "Path to a gene correlations file or folder. It's is mandatory if running a GLS model, and not necessary for OLS",
        "use_covars": "List of covariates to use",
        "cohort_name": "Cohort name",
        "lv_list": "List of LV (gene modules) identifiers on which an association will be computed. All the rest not in the list are ignored",
        "debug_use_sub_corr": "Use an LV-specific submatrix of the gene correlation matrix",       "model": "Choose which regression model to use",
        "batch_id": "Batch ID",
        "batch_n_splits": "Number of splits in the batch"
    }
)

RUN = ImmutableDict(
    {
        "gls": RUN_GLS
    }
)

CLI = ImmutableDict(
    {
        "run": RUN
    }
)

