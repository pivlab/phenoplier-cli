from types import MappingProxyType as ImmutableDict

# List of all supported covariates
COVAR_OPTIONS = [
    "all",
    "gene_size",
    "gene_size_log",
    "gene_density",
    "gene_density_log",
    "gene_n_snps_used",
    "gene_n_snps_used_log",
    "gene_n_snps_used_density",
    "gene_n_snps_used_density_log",
]

RUN_GLS_DEFAULTS = ImmutableDict(
    {
        "covars": "gene_size gene_size_log gene_density gene_density_log"
    }
)

RUN_GLS_ARGS = ImmutableDict(
    {
        "input_file": "File path to S-MultiXcan result file (tab-separated and with at least columns 'gene' and 'pvalue').",
        "output_file": "File path where results will be written to.",
        "project_dir": "Path to the project directory that contains initialized settings files and data. If not provided, will use the current directory.",
        "gene_corr_file": "Path to a gene correlations file or folder. It's is mandatory if running a GLS model, and not necessary for OLS.",
        "covars": f"List of covariates to use. Separate them by spaces. If provided with 'default', the default "
                  f"covariates will be used. Available covariates:[{' '.join(COVAR_OPTIONS)}]. And the default "
                  f"covariates are: [{RUN_GLS_DEFAULTS['covars']}].",
        "cohort_name": "Cohort name.",
        "lv_list": "List of LV (gene modules) identifiers on which an association will be computed. All the rest not in the list are ignored.",
        "lv_model_file": "A file containing the LV model. It has to be in pickle format, with gene symbols in rows and LVs in columns.",
        "debug_use_sub_corr": "Use an LV-specific submatrix of the gene correlation matrix.",
        "model": "Choose which regression model to use: [gls | ols].",
        "batch_id": "Batch ID.",
        "batch_n_splits": "Number of splits in the batch.",
        "dup_genes_action": "Mandatory if gene identifies are duplicated.",
    }
)

RUN = ImmutableDict(
    {
        "gls": RUN_GLS_ARGS
    }
)

INIT = ImmutableDict(
    {
        "project_dir": "Path to output the initialized project files. Default to current directory."
    }
)

CLI = ImmutableDict(
    {
        "version": "Print out the app's version."
    }
)