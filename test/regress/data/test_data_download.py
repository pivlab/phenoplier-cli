import tempfile
from pathlib import Path
from phenoplier.data import Downloader
from phenoplier.config import settings


def test_setup_test_data():
    downloader = Downloader()


    # Define the command with the script path variable
    actions = [
        "download_phenomexcan_rapid_gwas_pheno_info",
        "download_phenomexcan_rapid_gwas_data_dict_file",
        "download_uk_biobank_coding_3",
        "download_uk_biobank_coding_6",
        "download_phenomexcan_gtex_gwas_pheno_info",
        "download_gene_map_id_to_name",
        "download_gene_map_name_to_id",
        "download_biomart_genes_hg38",
        "download_multiplier_model_z_pkl"
    ]

    downloader.setup_data(actions=actions)