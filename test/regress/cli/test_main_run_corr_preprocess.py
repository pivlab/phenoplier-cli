import os

from typer.testing import CliRunner
from pytest import mark
from phenoplier import cli

runner = CliRunner()
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
_BASE_COMMAND_NAME = "run gene-corr"


@mark.parametrize("options, expected_output", [
    ([f"{_BASE_COMMAND_NAME} --help", f"{_BASE_COMMAND_NAME} -h"], ""),
    ([f"{_BASE_COMMAND_NAME} cov --help", f"{_BASE_COMMAND_NAME} cov -h"], ""),
    ([f"{_BASE_COMMAND_NAME} preprocess --help", f"{_BASE_COMMAND_NAME} preprocess -h"], ""),
    ([f"{_BASE_COMMAND_NAME} correlate --help", f"{_BASE_COMMAND_NAME} correlate -h"], ""),
    ([f"{_BASE_COMMAND_NAME} postprocess --help", f"{_BASE_COMMAND_NAME} postprocess -h"], ""),
    ([f"{_BASE_COMMAND_NAME} generate --help", f"{_BASE_COMMAND_NAME} generate -h"], ""),
])
def test_options(options, expected_output):
    for i in range(len(options)):
        result = runner.invoke(cli.app, options[i])
        assert result.exit_code == 0
        assert expected_output in result.stdout


# Define the placeholders in the command
_BASE_COMMAND = (
    "run gene-corr preprocess "
    "-c {cohort} "
    "-g {gwas_file} "
    "-s {spredixcan_dir} "
    "-n {output_file_name} "
    "-f {smultixcan_file} "
    "-r {reference_panel} "
    "-m {eqtl_models}"
)


@mark.skipif(IN_GITHUB_ACTIONS, reason="Data has not been setup in Github Actions yet. Local test only.")
# Parameterize the test cases
@mark.parametrize(
    "cohort, gwas_file, spredixcan_dir, output_file_name, smultixcan_file, reference_panel, eqtl_models",
    [
        (
                "1000g_eur",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/final_imputed_gwas/random.pheno0.glm-imputed.txt.gz",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/twas/spredixcan",
                "random.pheno0-gtex_v8-mashr-{tissue}.csv",
                "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/_previous_null_sims/twas/smultixcan/random.pheno0-gtex_v8-mashr-smultixcan.txt",
                "GTEX_V8",
                "MASHR"
        ),
        # Add more test cases here as needed
    ]
)
def test_cli_command(cohort, gwas_file, spredixcan_dir, output_file_name, smultixcan_file, reference_panel,
                     eqtl_models):
    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        gwas_file=gwas_file,
        spredixcan_dir=spredixcan_dir,
        output_file_name=output_file_name,
        smultixcan_file=smultixcan_file,
        reference_panel=reference_panel,
        eqtl_models=eqtl_models,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)

    # Assert the command ran successfully
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}\nOutput: {result.stdout}"
