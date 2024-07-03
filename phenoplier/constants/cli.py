"""
This module contains constants for the CLI commands. Mostly, it contains help messages for the CLI arguments.
"""

from enum import Enum
from typing import Annotated, List

import typer

from phenoplier.commands.util.enums import CovarOptions, Cohort


class Regression_Defaults(Enum):
    COVARS = "gene_size gene_size_log gene_density gene_density_log"


# Const help messages for common arguments
class Common_Args(Enum):
    PROJECT_DIR = typer.Option("--project-dir", "-p",
                               help="Path to output the initialized project files. Default to current directory.")
    COHORT_NAME = typer.Option("--cohort-name", "-c", help="Name of the cohort to use, such as 1000G or GTEX_V8.")
    REFERENCE_PANEL = typer.Option("--reference-panel", "-r",
                                   help="Name of the reference panel to use, such as MASHR or ELASTIC_NET.")
    EQTL_MODEL = typer.Option("--eqtl-model", "-m", help="Prediction models such as MASHR or ELASTIC_NET.")


# Const help messages for the main CLI arguments
class Cli(Enum):
    VERSION = "Print out the app's version."


class Corr_Correlate_Args(Enum):
    COHORT_NAME = Common_Args.COHORT_NAME.value
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    CHROMOSOME = typer.Option("--chromosome", "-s", help="Chromosome number (1-22).")
    SMULTIXCAN_CONDITION_NUMBER = typer.Option("--smultixcan-condition-number", "-n",
                                               help="S-MultiXcan condition number.")
    COMPUTE_WITHIN_DISTANCE = typer.Option("--compute-correlations-within-distance", "-w",
                                           help="Compute correlations within distance.")
    DEBUG_MODE = typer.Option("--debug", "-d", help="Run with debug mode.")
    PROJECT_DIR = Common_Args.PROJECT_DIR.value


class Corr_Cov_Args(Enum):
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    COVARIANCE_MATRIX_DTYPE = typer.Option("--covariance-matrix-dtype", "-t",
                                           help="The numpy dtype used for the covariance matrix.")
    PROJECT_DIR = Common_Args.PROJECT_DIR.value
    OUTPUT_DIR = typer.Option("--output-dir", "-o", help="Output directory for the covariance matrix. This argument supersedes the project configuration.")


class Corr_Filter_Args(Enum):
    COHORT_NAME = Common_Args.COHORT_NAME.value
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    DISTANCES = typer.Option("--distances", "-d", help="List of distances to generate correlation matrices for.")
    PROJECT_DIR = Common_Args.PROJECT_DIR.value


class Corr_Generate_Args(Enum):
    COHORT_NAME = Common_Args.COHORT_NAME.value
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    LV_CODE = typer.Option("--lv-code", "-l",
                           help="The code of the latent variable (LV) to compute the correlation matrix for.")
    LV_PERCENTILE = typer.Option("--lv-percentile", "-e", min=0.0, max=1.0,
                                 help="A number from 0.0 to 1.0 indicating the top percentile of the genes in the LV "
                                      "to keep")
    PROJECT_DIR = Common_Args.PROJECT_DIR.value


class Corr_Postprocess_Args(Enum):
    COHORT_NAME = Common_Args.COHORT_NAME.value
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    PLOT_OUTPUT_DIR = typer.Option("--plot-output-dir", "-o", help="Output directory for plots.")
    PROJECT_DIR = Common_Args.PROJECT_DIR.value


class Corr_Preprocess_Args(Enum):
    COHORT_NAME = Common_Args.COHORT_NAME.value
    GWAS_FILE = typer.Option("--gwas-file", "-g", help="GWAS file.")
    SPREDIXCAN_FOLDER = typer.Option("--spredixcan-folder", "-s", help="S-PrediXcan folder.")
    SPREDIXCAN_FILE_PATTERN = typer.Option("--spredixcan-file-pattern", "-n", help="S-PrediXcan file pattern.")
    SMULTIXCAN_FILE = typer.Option("--smultixcan-file", "-f", help="S-MultiXcan file.")
    REFERENCE_PANEL = Common_Args.REFERENCE_PANEL.value
    EQTL_MODEL = Common_Args.EQTL_MODEL.value
    PROJECT_DIR = Common_Args.PROJECT_DIR.value


class Regression_Args(Enum):
    INPUT_FILE = typer.Option("--input-file", "-i",
                              help="File path to S-MultiXcan result file (tab-separated and with at least columns "
                                   "'gene' and 'pvalue').")

    OUTPUT_FILE = typer.Option("--output-file", "-o",
                               help="File path where results will be written to.")

    PROJECT_DIR = Common_Args.PROJECT_DIR.value

    MODEL = typer.Option("--model",
                         help="Choose which regression model to use. OLS is usually used for debugging / comparison "
                              "purpose.")

    GENE_CORR_FILE = typer.Option("--gene-corr-file", "-g",
                                  help="Path to a gene correlations file or folder. It's mandatory if running a GLS "
                                       "model, and not necessary for OLS.")

    GENE_CORR_MODE = typer.Option("--gene-corr-mode", "-m",
                                  help="Use an LV-specific submatrix of the gene correlation matrix.")

    DUP_GENES_ACTION = typer.Option("--dup-genes-action", "-d",
                                    help="Decide how to deal with duplicate gene entries in the input file. Mandatory "
                                         "if gene identifies are duplicated.")

    COVARS = typer.Option("--covars", "-c",
                          help="List of covariates to use. Separate them by spaces. If provided with 'default', "
                               "the default covariates will be used."
                               f"Available covariates: {[covar.name.lower() for covar in CovarOptions]}. "
                               f"And the default covariates are: [{CovarOptions.DEFAULT.value}].")

    COHORT_METADATA_DIR = typer.Option("--cohort-metadata-dir", "-t",
                                       help="Directory where cohort metadata files are stored.")

    LV_LIST = typer.Option("--lv-list", "-l",
                           help="List of LV (gene modules) identifiers on which an association will be computed. All "
                                "the rest not in the list are ignored.")

    LV_MODEL_FILE = typer.Option("--lv-model-file", "-f",
                                 help="A file containing the LV model. It has to be in pickle format, with gene "
                                      "symbols in rows and LVs in columns.")

    BATCH_ID = typer.Option("--batch-id", "-b",
                            help="With --batch-n-splits, it allows to distribute computation of each LV-trait pair "
                                 "across a set of batches.")

    BATCH_N_SPLITS = typer.Option("--batch-n-splits", "-n",
                                  help="With --batch-id, it allows to distribute computation of each LV-trait pair "
                                       "across a set of batches.")


# Const help messages for the "run" command
class Run_Args(Enum):
    REGRESSION = Regression_Args
