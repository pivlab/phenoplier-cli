from enum import Enum
from pathlib import Path
from typing import Annotated
import typer
from phenoplier.data import Downloader
from phenoplier.commands.utils import load_settings_files
from phenoplier.cli_constants import CLI, INIT
from phenoplier.config import settings as conf


class DownloadAction(str, Enum):
    test_data = "test_data"
    full_data = "full_data"


test_actions = [
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
]

ActionMap = {
    DownloadAction.test_data: test_actions,
    DownloadAction.full_data: test_actions,
}


def get(
    mode: Annotated[DownloadAction, typer.Argument()],
    project_dir: Annotated[Path, typer.Option("--project-dir", "-p", help=INIT["project_dir"])] = conf.CURRENT_DIR
):
    """
    Download necessary data for running PhenoPLIER's pipelines.
    """
    load_settings_files(project_dir)
    downloader = Downloader()
    actions = ActionMap.get(mode)
    downloader.setup_data(actions=actions)
