# import os
# from pathlib import Path
# import logging
#
# from typer.testing import CliRunner
# from pytest import mark
#
# from phenoplier import cli
# from phenoplier.config import settings as conf
# from phenoplier.commands.invoker import invoke_corr_preprocess
# from test.utils import get_test_output_dir, compare_dataframes_equal, load_pickle
#
# logger = logging.getLogger(__name__)
#
# runner = CliRunner()
# IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
#
# # Define the placeholders in the command
# _BASE_COMMAND = (
#     "run gene-corr pipeline "
#     "-c {cohort} "
#     "-r {reference_panel} "
#     "-m {eqtl_model} "
#     "-g {gwas_file} "
#     "-s {spredixcan_folder} "
#     "-n {spredixcan_file_pattern} "
#     "-f {smultixcan_file} "
#     "-o {output_dir} "
# )
#
# # Define the test output directory
# # Todo: organize test data dir the same way as test output dir
# output_dir_base = get_test_output_dir(Path(__file__))
# test_data_dir = Path(conf.TEST_DIR) / "data/gene-corr/99_all_results/mashr/"
#
#
# @mark.skipif(IN_GITHUB_ACTIONS, reason="Data has not been setup in Github Actions yet. Local test only.")
# @mark.corr
# # Parameterize the test cases
# @mark.parametrize(
#     "cohort, reference_panel, eqtl_model, "  # Command options
#     "gwas_file, spredixcan_folder, spredixcan_file_pattern, smultixcan_file, "  # Preprocess options
#     "output_dir",  # Command options with default values
#     [
#         (
#                 "phenomexcan_rapid_gwas",
#                 "GTEX_V8",
#                 "MASHR",
#                 "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gwas_parsing/full/22617_7112.txt.gz",
#                 "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/spredixcan/rapid_gwas_project/22617_7112",
#                 "22617_7112-gtex_v8-{tissue}-2018_10.csv",
#                 "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/data/phenomexcan/gene_assoc/smultixcan/rapid_gwas_project/smultixcan_22617_7112_ccn30.tsv.gz",
#                 output_dir_base
#         ),
#         # Add more test cases here as needed
#     ]
# )
# def test_cli_command(cohort,
#                      reference_panel,
#                      eqtl_model,
#                      gwas_file,
#                      spredixcan_folder,
#                      spredixcan_file_pattern,
#                      smultixcan_file,
#                      output_dir):
#     # -p <project_dir> is omitted here
#     command = _BASE_COMMAND.format(
#         cohort=cohort,
#         reference_panel=reference_panel,
#         eqtl_model=eqtl_model,
#         gwas_file=gwas_file,
#         spredixcan_folder=spredixcan_folder,
#         spredixcan_file_pattern=spredixcan_file_pattern,
#         smultixcan_file=smultixcan_file,
#         output_dir=output_dir,
#     )
#     print(output_dir)
#     print(f"Testing command: {command}")
#     result = runner.invoke(cli.app, command)
#     assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"
