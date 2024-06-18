"""
This module contains constants for the CLI commands. Mostly, it contains help messages for the CLI arguments.
"""

from enum import Enum

from phenoplier.commands.util.enums import CovarOptions


class Regression_Defaults(Enum):
    COVARS = "gene_size gene_size_log gene_density gene_density_log"


# Const help messages for the "run regression" command
class Regression_Args(Enum):
    INPUT_FILE = (
        "File path to S-MultiXcan result file (tab-separated and with at least columns 'gene' and 'pvalue')."
    )
    DUP_GENES_ACTION = (
        "Decide how to deal with duplicate gene entries in the input file. Mandatory if gene identifies are duplicated."
    )
    OUTPUT_FILE = "File path where results will be written to."
    PROJECT_DIR = (
        "Path to the project directory that contains initialized settings files and data. If not provided, will use the current shell directory."
    )
    GENE_CORR_FILE = (
        "Path to a gene correlations file or folder. It's mandatory if running a GLS model, and not necessary for OLS."
    )
    COVARS = (
        "List of covariates to use. Separate them by spaces. If provided with 'default', the default covariates will be used. "
        f"Available covariates: {[covar.name.lower() for covar in CovarOptions]}. "
        f"And the default covariates are: [{CovarOptions.DEFAULT.value}]."
    )
    COHORT_METADATA_DIR = "Directory where cohort metadata files are stored."
    LV_LIST = (
        "List of LV (gene modules) identifiers on which an association will be computed. All the rest not in the list are ignored."
    )
    LV_MODEL_FILE = (
        "A file containing the LV model. It has to be in pickle format, with gene symbols in rows and LVs in columns."
    )
    DEBUG_USE_SUB_CORR = "Use an LV-specific submatrix of the gene correlation matrix."
    MODEL = (
        "Choose which regression model to use. OLS is usually used for debugging / comparison purpose."
    )
    BATCH_ID = (
        "With --batch-n-splits, it allows to distribute computation of each LV-trait pair across a set of batches."
    )
    BATCH_N_SPLITS = (
        "With --batch-id, it allows to distribute computation of each LV-trait pair across a set of batches."
    )


# Const help messages for the "run" command
class Run_Args(Enum):
    REGRESSION = Regression_Args


# Const help messages for common arguments
class Common_Args(Enum):
    PROJECT_DIR = "Path to output the initialized project files. Default to current directory."


# Const help messages for the main CLI arguments
class Cli(Enum):
    VERSION = "Print out the app's version."

