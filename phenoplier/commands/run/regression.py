"""
This module contains the CLI command to run the LV-trait regression.
"""

import sys
import logging
from typing import Optional, Annotated, List
from pathlib import Path
from enum import Enum, StrEnum

import typer
import pandas as pd
import numpy as np
from rich import print

from phenoplier.gls import GLSPhenoplier
from phenoplier.config import settings, SETTINGS_FILES
from phenoplier.constants.arg import Regression_Args as Args, Regression_Defaults
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.message import RegressionError as err
from phenoplier.constants.message import RegressionInfo as info

LOG_FORMAT = "%(levelname)s: %(message)s"

h1 = logging.StreamHandler(stream=sys.stdout)
h1.setLevel(logging.INFO)
h1.addFilter(lambda record: record.levelno <= logging.INFO)
h2 = logging.StreamHandler()
h2.setLevel(logging.WARNING)

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, handlers=[h1, h2])
logger = logging.getLogger("root")

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

COVAR_OPTIONS_DEFAULT = [
    "gene_size",
    "gene_size_log",
    "gene_density",
    "gene_density_log",
]

# Subset of covariates taht need SNP-level information
SNPLEVEL_COVAR_OPTIONS_PREFIXES = [
    "gene_n_snps_used",
    "gene_n_snps_used_density",
]


class DUP_GENE_ACTIONS(StrEnum):
    keep_first = "keep-first"
    keep_last = "keep-last"
    remove_all = "remove-all"
    no_action = "no-action"


class REGRESSION_MODEL(StrEnum):
    gls = "gls"
    ols = "ols"


class GENE_CORREALATION_MODE(StrEnum):
    sub = "sub"
    full = "full"


def check_config_files(dir: str) -> None:
    for file_name in SETTINGS_FILES:
        settings_file = Path(dir) / file_name
        if not settings_file.exists():
            raise typer.BadParameter(
                f"Config file {str(file_name)} does not exist at {dir}. Please run 'phenoplier init' first.")


def regression(
        input_file: Annotated[Path, Args.INPUT_FILE.value],
        output_file: Annotated[Path, Args.OUTPUT_FILE.value],
        project_dir: Annotated[str, Args.PROJECT_DIR.value] = settings.CURRENT_DIR,
        model: Annotated[REGRESSION_MODEL, Args.MODEL.value] = REGRESSION_MODEL.gls,
        gene_corr_file: Annotated[Optional[Path], Args.GENE_CORR_FILE.value] = None,
        gene_corr_mode: Annotated[GENE_CORREALATION_MODE, Args.GENE_CORR_MODE.value] = GENE_CORREALATION_MODE.full,
        dup_genes_action: Annotated[DUP_GENE_ACTIONS, Args.DUP_GENES_ACTION.value] = DUP_GENE_ACTIONS.no_action,
        covars: Annotated[Optional[str], Args.COVARS.value] = None,
        cohort_metadata_dir: Annotated[Optional[str], Args.COHORT_METADATA_DIR.value] = None,
        lv_list: Annotated[Optional[str], Args.LV_LIST.value] = None,
        lv_model_file: Annotated[Optional[Path], Args.LV_MODEL_FILE.value] = None,
        batch_id: Annotated[Optional[int], Args.BATCH_ID.value] = None,
        batch_n_splits: Annotated[Optional[int], Args.BATCH_N_SPLITS.value] = None,
) -> None:
    """
    Run the Generalized Least Squares (GLS) model by default. Note that you need to run "phenoplier init" first to set up the environment.
    """

    def check_batch_args():
        if lv_list and (batch_id is not None or batch_n_splits is not None):
            print(err.INCOMPATIBLE_BATCH_ID_AND_LV_LIST)
            exit(2)

        if (batch_id is not None and batch_n_splits is None) or (
                batch_id is None and batch_n_splits is not None
        ):
            print(err.EXPECT_BOTH_BATCH_ARGS)
            exit(2)

        if batch_id is not None and batch_id < 1:
            print(err.EXPECT_BATCH_ID_GT_ZERO)
            exit(2)

        if (
                batch_id is not None
                and batch_n_splits is not None
                and batch_id > batch_n_splits
        ):
            print(err.INCOMPATIBLE_BATCH_ARGS)
            exit(2)

    # Todo: Use enums to store echo messages, can be reused in tests
    def check_output_file():
        if output_file.exists():
            print(f"Skipping, output file exists: {str(output_file)}")
            # logger.info(f"Skipping, output file exists: {str(output_file)}")
            raise typer.Exit(0)
        if not output_file.parent.exists():
            print(f"Error: parent directory of output file does not exist: {str(output_file.parent)}")
            # logger.error(f"Parent directory of output file does not exist: {str(output_file.parent)}")
            raise typer.Exit(1)

    def check_model_args():
        # Check if both "debug_use_ols" and "gene_corr_file" are None
        if model != "ols" and gene_corr_file is None:
            print(err.EXPECT_GENE_CORR_FILE)
            exit(2)
        # and they should not be both provided
        if model == "ols" and gene_corr_file is not None:
            # Todo: can print a message to tell the user that the gene_corr_file will be ignored
            print(err.EXPECT_NO_GENE_CORR_FILE)
            exit(2)

    def read_input() -> pd.DataFrame:
        data = pd.read_csv(input_file, sep="\t")
        print(info.LOADING_INPUT)
        print(f"Input file has {data.shape[0]} genes")

        if "gene_name" not in data.columns:
            # logger.error("Mandatory columns not present in data 'gene_name'")
            print(err.NO_GENE_NAME_COLUMN)
            sys.exit(1)

        if "pvalue" not in data.columns:
            print(err.NO_P_VALUE_COLUMN)
            # logger.error("Mandatory columns not present in data 'pvalue'")
            sys.exit(1)

        data = data.set_index("gene_name")
        return data

    def remove_dup_gene_entries(input_data: pd.DataFrame) -> (pd.DataFrame, bool):
        if dup_genes_action is DUP_GENE_ACTIONS.no_action:
            return input_data, False

        if dup_genes_action.startswith("keep"):
            action = dup_genes_action.split("-")[1]
        elif dup_genes_action == "remove-all":
            action = False
        else:
            raise ValueError("Wrong --dup-gene-action value")

        dedup_data = input_data.loc[~input_data.index.duplicated(keep=action)]
        print(
            f"Removed duplicated genes symbols using '{dup_genes_action}'. "
            f"Data now has {dedup_data.shape[0]} genes"
        )
        return dedup_data, action

    # Check arguments
    check_batch_args()
    check_model_args()
    check_output_file()

    # Load config files
    load_settings_files(Path(project_dir))

    # Load input data
    data = read_input()
    data, keep_action = remove_dup_gene_entries(data)
    # unique index (gene names)
    if not data.index.is_unique:
        # logger.error(
        #     "Duplicated genes in input data. Use option --dup-gene-action "
        #     "if you want to skip them."
        # )
        print(err.DUP_GENES_FOUND)
        sys.exit(1)

    # Print out useful information
    covars_info = (
        f"Using DEFAULT covariates: {Regression_Defaults.COVARS.value}" if covars == "default"
        else f"Using covariates {covars}" if covars
        else f"Running {model} without covariates."
    )
    print("[blue][Info]: " + covars_info)
    # pvalues statistics
    _data_pvalues = data["pvalue"]
    n_missing = _data_pvalues.isna().sum()
    n = _data_pvalues.shape[0]
    min_pval = _data_pvalues.min()
    mean_pval = _data_pvalues.mean()
    max_pval = _data_pvalues.max()

    # logger.info(
    #     f"p-values statistics: min={min_pval:.1e} | mean={mean_pval:.1e} | max={max_pval:.1e} | # missing={n_missing} ({(n_missing / n) * 100:.1f}%)"
    # )
    print(f"p-values statistics: "
          f"min={min_pval:.1e} | "
          f"mean={mean_pval:.1e} | "
          f"max={max_pval:.1e} | "
          f"# missing={n_missing} ({(n_missing / n) * 100:.1f}%)")

    if min_pval < 0.0:
        # logger.warning("Some p-values are smaller than 0.0")
        print("Some p-values are smaller than 0.0")

    if max_pval > 1.0:
        print("Some p-values are greater than 1.0")
        # logger.warning("Some p-values are greater than 1.0")

    final_data = data.loc[:, ["pvalue"]].rename(
        columns={
            "pvalue": "y",
        }
    )

    # Add covariates (if specified)
    if covars is not None:
        covars_selected = str.split(covars, " ")
        print("Covars selected: ", covars)

        if "all" in covars_selected:
            covars_selected = [c for c in COVAR_OPTIONS if c != "all"]

        if "default" in covars_selected:
            covars_selected = COVAR_OPTIONS_DEFAULT

        covars_selected = sorted(covars_selected)

        # logger.info(f"Using covariates: {covars_selected}")
        print(f"Using covariates: {covars_selected}")

        # get necessary columns from results
        covars = data[["pvalue", "n", "n_indep"]]
        covars = covars.rename(
            columns={
                "n_indep": "gene_size",
            }
        )

        if "gene_density" in covars_selected:
            covars = covars.assign(
                gene_density=covars.apply(lambda x: x["gene_size"] / x["n"], axis=1)
            )

        # process snp-level covariates
        if any(
                c.startswith(snplevel_c)
                for c in covars_selected
                for snplevel_c in SNPLEVEL_COVAR_OPTIONS_PREFIXES
        ):
            # first load the cohort metadata gene tissues file
            if cohort_metadata_dir is None:
                # logger.error(
                #     "To use SNP-level covariates, a cohort metadata folder must "
                #     "be provided (--cohort-metadata-dir)"
                # )
                print(
                    "To use SNP-level covariates, a cohort metadata folder must "
                    "be provided (--cohort-metadata-dir)"
                )
                sys.exit(1)

            cohort_metadata_dir = Path(cohort_metadata_dir).resolve()
            cohort_gene_tissues_filepath = cohort_metadata_dir / "gene_tissues.pkl"
            if not cohort_gene_tissues_filepath.exists():
                cohort_gene_tissues_filepath = cohort_gene_tissues_filepath.with_suffix(
                    ".pkl.gz"
                )
                assert cohort_gene_tissues_filepath.exists(), (
                    f"No gene_tissues.pkl[.gz] exists in cohort metadata folder: "
                    f"{cohort_metadata_dir}"
                )

            # logger.info(f"Loading cohort metadata: {str(cohort_gene_tissues_filepath)}")
            print(f"Loading cohort metadata: {str(cohort_gene_tissues_filepath)}")
            cohort_gene_tissues = pd.read_pickle(
                cohort_gene_tissues_filepath
            ).set_index("gene_name")
            # remove duplicated gene names
            if not cohort_gene_tissues.index.is_unique:
                if dup_genes_action is None:
                    # logger.error(
                    #     "There are duplicated gene names in cohort metadat files, --dup-gene-action must be specified"
                    # )
                    print(
                        "There are duplicated gene names in cohort metadat files, --dup-gene-action must be specified")
                    sys.exit(1)

                cohort_gene_tissues = cohort_gene_tissues.loc[
                    ~cohort_gene_tissues.index.duplicated(keep=keep_action)
                ]

            common_genes = final_data.index.intersection(cohort_gene_tissues.index)
            cohort_gene_tissues = cohort_gene_tissues.loc[common_genes]

            # check individual covariates
            if "gene_n_snps_used" in covars_selected:
                covars = covars.assign(
                    gene_n_snps_used=cohort_gene_tissues["n_snps_used_sum"]
                )

            if "gene_n_snps_used_density" in covars_selected:
                covars = covars.assign(
                    gene_n_snps_used_density=cohort_gene_tissues.apply(
                        lambda x: x["n_snps_used_sum"] / x["unique_n_snps_used"],
                        axis=1,
                    )
                )

        # add log versions of covariates (if specified)
        for c in covars_selected:
            if c.endswith("_log"):
                c_prefix = c.split("_log")[0]

                if c_prefix not in covars.columns:
                    # logger.error(
                    #     f"If log version of covar is selected, covar has to be "
                    #     f"selected as well ({c_prefix} not present)"
                    # )
                    print(
                        f"If log version of covar is selected, covar has to be "
                        f"selected as well ({c_prefix} not present)"
                    )
                    sys.exit(1)

                covars[c] = np.log(covars[c_prefix])
                if "density" in c_prefix:
                    covars[c] = -1 * covars[c]

        final_data = pd.concat([final_data, covars[covars_selected]], axis=1)

    # convert p-values
    # logger.info("Replacing zero p-values by nonzero minimum divided by 10")
    print("Replacing zero p-values by nonzero minimum divided by 10")
    min_nonzero_pvalue = final_data[final_data["y"] > 0]["y"].min() / 10.0
    final_data["y"] = final_data["y"].replace(0, min_nonzero_pvalue)

    # logger.info("Using -log10(pvalue)")
    print("Using -log10(pvalue)")
    final_data["y"] = -np.log10(final_data["y"])

    if final_data.shape[1] == 1:
        final_data = final_data.squeeze().rename(input_file.stem)

    if gene_corr_file is not None:
        # logger.info(f"Using gene correlation file: {gene_corr_file}")
        print(f"Using gene correlation file: {gene_corr_file}")

    if lv_model_file is not None:
        lv_model_file = Path(lv_model_file)
        # logger.info(f"Reading LV model file: {str(lv_model_file)}")
        print(f"Reading LV model file: {str(lv_model_file)}")
        full_lvs_list = GLSPhenoplier._get_lv_weights(lv_model_file).columns.tolist()
    else:
        full_lvs_list = GLSPhenoplier._get_lv_weights().columns.tolist()

    if batch_n_splits is not None and batch_n_splits > len(full_lvs_list):
        print(err.EXPECT_BATCH_N_SPLITS_LT_LVS)
        # logger.error(
        #     f"--batch-n-splits cannot be greater than LVs in the model "
        #     f"({len(full_lvs_list)} LVs)"
        # )
        sys.exit(2)

    full_lvs_set = set(full_lvs_list)
    # logger.info(f"{len(full_lvs_set)} LVs (gene modules) were found in LV model")
    print(f"{len(full_lvs_set)} LVs (gene modules) were found in LV model")

    if lv_list:
        selected_lvs = [lv for lv in lv_list if lv in full_lvs_set]
        print(
            f"A list of {len(lv_list)} LVs was provided, and {len(selected_lvs)} "
            f"are present in LV models"
        )
        # logger.info(
        #     f"A list of {len(lv_list)} LVs was provided, and {len(selected_lvs)} "
        #     f"are present in LV models"
        # )
    else:
        selected_lvs = full_lvs_list
        print("All LVs in models will be used")
        logger.info("All LVs in models will be used")

    if batch_id is not None and batch_n_splits is not None:
        selected_lvs_chunks = [
            ar.tolist() for ar in np.array_split(selected_lvs, batch_n_splits)
        ]
        selected_lvs = selected_lvs_chunks[batch_id - 1]
        print(f"Using batch {batch_id} out of {batch_n_splits} ({len(selected_lvs)} LVs selected)")
        # logger.info(
        #     f"Using batch {batch_id} out of {batch_n_splits} ({len(selected_lvs)} LVs selected)"
        # )

    if len(selected_lvs) == 0:
        print("No LVs were selected")
        # logger.error("No LVs were selected")
        sys.exit(1)

    print(model)
    print(gene_corr_mode)
    # create model object
    gls_model = GLSPhenoplier(
        gene_corrs_file_path=gene_corr_file,
        debug_use_ols=True if model == "ols" else False,
        debug_use_sub_gene_corr=True if gene_corr_mode == "sub" else False,
        use_own_implementation=True,
        logger=logger,
    )

    results = []

    # compute an association between each LV and the gene-trait associations
    for lv_idx, lv_code in enumerate(selected_lvs):
        print(f"Computing for {lv_code}")
        # logger.info(f"Computing for {lv_code}")

        # show warnings or logs only in the first run
        if lv_idx == 0:
            gls_model.set_logger(logger)
        elif lv_idx == 1:
            gls_model.set_logger(None)

        gls_model.fit_named(lv_code, final_data)

        res = gls_model.results

        results.append(
            {
                "lv": lv_code,
                "beta": res.params.loc["lv"],
                "beta_se": res.bse.loc["lv"],
                "t": res.tvalues.loc["lv"],
                # "pvalue_twosided": res.pvalues.loc["lv"],
                "pvalue": res.pvalues_onesided.loc["lv"],
            }
        )

    # create final dataframe and save
    results = pd.DataFrame(results).set_index("lv").sort_values("pvalue")
    print(f"Writing results to {str(output_file)}")
    # logger.info(f"Writing results to {str(output_file)}")
    results.to_csv(output_file, sep="\t", na_rep="NA")
