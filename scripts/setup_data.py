from phenoplier.data import Downloader


def setup_test_data():
    downloader = Downloader()

    # Specify the test directory
    # os.environ["PHENOPLIER_ROOT_DIR"] = str(Path('/tmp/pptest/').resolve())
    # print(os.environ.get("PHENOPLIER_ROOT_DIR"))
    # importlib.reload(importlib.import_module("phenoplier.config"))
    # print()
    # print(settings.ROOT_DIR)
    # print()

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
        "download_multiplier_model_z_pkl",
        "download_snps_covariance_1000g_mashr",
        "download_predixcan_mashr_prediction_models",
    ]

    downloader.setup_data(actions=actions)


if __name__ == "__main__":
    setup_test_data()
