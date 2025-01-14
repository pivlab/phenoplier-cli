"""
This module is a sub-command of the main CLI. It downloads necessary data for running PhenoPLIER's pipelines.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated
import typer
from phenoplier.data import Downloader
from phenoplier.commands.util.utils import load_settings_files
from phenoplier.constants.arg import Common_Args
from phenoplier.config import settings as conf
from phenoplier.commands.util.enums import DownloadAction

# Common actions shared between test_actions and ci_test_actions
common_actions = [
    "download_phenomexcan_rapid_gwas_pheno_info",
    "download_phenomexcan_rapid_gwas_data_dict_file",
    "download_uk_biobank_coding_3",
    "download_uk_biobank_coding_6",
    "download_phenomexcan_gtex_gwas_pheno_info",
    "download_gene_map_id_to_name",
    "download_gene_map_name_to_id",
    "download_biomart_genes_hg38",
    "download_multiplier_model_z_pkl",
    "download_snps_covariance_gtex_mashr",
    "download_snps_covariance_1000g_mashr",
    "download_predixcan_mashr_prediction_models",
    "download_multiplier_model_metadata_pkl",
]

# Unique actions for test_actions
test_unique_actions = [
    "download_reference_panel_gtex_v8",
]

# Construct lists using common actions and unique actions
test_actions = common_actions + test_unique_actions
ci_test_actions = common_actions


full_actions = test_actions + [
    "download_smultixcan_results",
]

smul_data = [
    "download_smultixcan_results",
]

t21_actions = [
    "download_phenomexcan_rapid_gwas_pheno_info",
    "download_phenomexcan_rapid_gwas_data_dict_file",
    "download_uk_biobank_coding_3",
    "download_uk_biobank_coding_6",
    "download_phenomexcan_gtex_gwas_pheno_info",
    "download_gene_map_id_to_name",
    "download_gene_map_name_to_id",
    "download_biomart_genes_hg38",
    # "download_multiplier_model_z_pkl",
    "download_snps_covariance_gtex_mashr",
    # "download_snps_covariance_1000g_mashr",
    "download_predixcan_mashr_prediction_models",
    # "download_smultixcan_results",
    "download_smultiscan_results_zip",
    "download_reference_panel_gtex_v8",
]

nullsim_twas = [
    "download_1000g_genotype_data",
    "download_liftover_hg19tohg38_chain",
    "download_eur_ld_regions",
    "download_setup_summary_gwas_imputation"
]

ActionMap = {
    DownloadAction.test_data: test_actions,
    DownloadAction.full_data: full_actions,
    DownloadAction.smul_data: smul_data,
    DownloadAction.t21_data: t21_actions,
    DownloadAction.ci_test_data: ci_test_actions,
    DownloadAction.nullsim_twas: nullsim_twas
}


def get(
    mode: Annotated[DownloadAction, typer.Argument()],
    project_dir: Annotated[Path, Common_Args.PROJECT_DIR.value] = conf.CURRENT_DIR
):
    """
    Download necessary data for running PhenoPLIER's pipelines.
    """
    load_settings_files(project_dir)
    downloader = Downloader()
    actions = ActionMap.get(mode)
    downloader.setup_data(actions=actions)
