# import tempfile
# from pathlib import Path
# from typer.testing import CliRunner
# from phenoplier import cli
# from phenoplier.data import setup_data
# from phenoplier.config import settings
#
# runner = CliRunner()
#
#
# def test_setup_test_data():
#     from importlib import reload, import_module
#     # TODO: change dir suffix to current test's relative path
#     parent_dir = Path(__file__).resolve().parent
#     output_file = Path("/tmp/ptest").resolve()
#     settings.ROOT_DIR = output_file
#     reload(import_module(".config", package="phenoplier"))
#
#     # Define the command with the script path variable
#     actions = [
#         "download_phenomexcan_rapid_gwas_pheno_info",
#         "download_phenomexcan_rapid_gwas_data_dict_file",
#         "download_uk_biobank_coding_3",
#         "download_uk_biobank_coding_6",
#         "download_phenomexcan_gtex_gwas_pheno_info",
#         "download_gene_map_id_to_name",
#         "download_gene_map_name_to_id",
#         "download_biomart_genes_hg38",
#         "download_multiplier_model_z_pkl"
#     ]
#
#     setup_data(actions=actions)