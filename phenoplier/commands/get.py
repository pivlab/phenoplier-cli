from enum import Enum
from typing import Annotated
import typer
from phenoplier.data import Downloader


class DownloadAction(str, Enum):
    test = "test"
    dev = "dev"
    full = "full"


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
    DownloadAction.test: test_actions,
}


def get(mode: Annotated[DownloadAction, typer.Argument()]):
    downloader = Downloader()
    actions = ActionMap.get(mode)
    downloader.setup_data(actions=actions)
