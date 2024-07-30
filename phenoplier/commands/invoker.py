"""
This module contains encapsulated function calls to invoke individual cli commands. Useful for pipeline automation
and testing.
"""
from pathlib import Path
from typing import Tuple, List

from typer.testing import CliRunner

from phenoplier import cli
from phenoplier.config import settings as conf
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel

runner = CliRunner()


# @formatter:off
def invoke_corr_preprocess(
        cohort:                     Cohort,
        gwas_file:                  Path,
        spredixcan_folder:          Path,
        spredixcan_file_pattern:    str,
        smultixcan_file:            Path,
        reference_panel:            RefPanel,
        eqtl_model:                 EqtlModel,
        output_dir:                 Path,
        project_dir:                Path = conf.CURRENT_DIR,
        ) -> Tuple[int, str]:
    # @formatter:on
    """
    Invokes the gene-corr preprocess command with the given arguments.
    """
    _BASE_COMMAND = (
        "run gene-corr preprocess "
        "-c {cohort} "
        "-r {reference_panel} "
        "-m {eqtl_model} "
        "-g {gwas_file} "
        "-s {spredixcan_folder} "
        "-n {spredixcan_file_pattern} "
        "-f {smultixcan_file} "
        "-p {project_dir} "
        "-o {output_dir} "
    )

    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        gwas_file=gwas_file,
        spredixcan_folder=spredixcan_folder,
        spredixcan_file_pattern=spredixcan_file_pattern,
        smultixcan_file=smultixcan_file,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        project_dir=project_dir,
        output_dir=output_dir,
    )
    result = runner.invoke(cli.app, command)
    success = result.exit_code == 0
    message = result.stdout

    gene_tissues_filename = "gene_tissues.pkl"
    test_gene_tissues = output_dir / gene_tissues_filename
    assert test_gene_tissues.exists(), f"gene-tissues.pkl not found in {output_dir}"

    return success, message


# @formatter:off
def invoke_corr_correlate(
        cohort:                         Cohort,
        reference_panel:                RefPanel,
        eqtl_model:                     EqtlModel,
        chromosome:                     int,
        smultixcan_condition_number:    int = 30,
        compute_within_distance:        bool = False,
        debug_mode:                     bool = False,
        input_dir:                      Path = None,
        output_dir:                     Path = None,
        project_dir:                    Path = conf.CURRENT_DIR,
) -> Tuple[int, str]:
    # @formatter:on
    """
    Invokes the gene-corr correlate command with the given arguments.
    """
    _BASE_COMMAND = (
        "run gene-corr correlate "
        "-c {cohort} "
        "-r {reference_panel} "
        "-m {eqtl_model} "
        "-s {chromosome} "
        "-i {input_dir} "
        "-p {project_dir} "
        "-o {output_dir} "
    )

    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        chromosome=chromosome,
        smultixcan_condition_number=smultixcan_condition_number,
        compute_within_distance=compute_within_distance,
        debug_mode=debug_mode,
        input_dir=input_dir,
        output_dir=output_dir,
        project_dir=project_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    success = result.exit_code == 0
    message = result.stdout
    return success, message


# @formatter:off
def invoke_corr_postprocess(
        cohort:                         Cohort,
        reference_panel:                RefPanel,
        eqtl_model:                     EqtlModel,
        input_dir:                      Path = None,
        genes_info:                     Path = None,
        output_dir:                     Path = None,
        project_dir:                    Path = conf.CURRENT_DIR,
) -> Tuple[int, str]:
    # @formatter:on
    """
    Invokes the gene-corr correlate command with the given arguments.
    """
    _BASE_COMMAND = (
        "run gene-corr postprocess "
        "-c {cohort} "
        "-r {reference_panel} "
        "-m {eqtl_model} "
        "-i {input_dir} "
        "-g {genes_info} "
        "-o {output_dir} "
    )

    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        input_dir=input_dir,
        genes_info=genes_info,
        output_dir=output_dir,
        project_dir=project_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    success = result.exit_code == 0
    message = result.stdout
    return success, message


# @formatter:off
def invoke_corr_filter(
        cohort:                         Cohort,
        reference_panel:                RefPanel,
        eqtl_model:                     EqtlModel,
        distances:                      List[float] = [10, 5, 2],
        genes_symbols:                  Path = None,
        output_dir:                     Path = None,
        project_dir:                    Path = conf.CURRENT_DIR,
) -> Tuple[int, str]:
    # @formatter:on
    """
    Invokes the gene-corr correlate command with the given arguments.
    """
    _BASE_COMMAND = (
        "run gene-corr filter "
        "-c {cohort} "
        "-r {reference_panel} "
        "-m {eqtl_model} "
        "-d {distances} "
        "-g {genes_symbols} "
        "-o {output_dir} "
    )

    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        distances=distances,
        genes_symbols=genes_symbols,
        output_dir=output_dir,
        project_dir=project_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    success = result.exit_code == 0
    message = result.stdout
    return success, message


# @formatter:off
def invoke_corr_generate(
        cohort:                         Cohort,
        reference_panel:                RefPanel,
        eqtl_model:                     EqtlModel,
        lv_code:                        int,
        lv_percentile:                  float = 0.05,
        genes_symbols_dir:              Path = None,
        output_dir:                     Path = None,
        project_dir:                    Path = conf.CURRENT_DIR,
) -> Tuple[int, str]:
    # @formatter:on
    """
    Invokes the gene-corr correlate command with the given arguments.
    """
    _BASE_COMMAND = (
        "run gene-corr generate "
        "-c {cohort} "
        "-r {reference_panel} "
        "-m {eqtl_model} "
        "-l {lv_code} "
        "-e {lv_percentile} "
        "-g {genes_symbols_dir} "
        "-o {output_dir} "
    )

    # Build the command
    command = _BASE_COMMAND.format(
        cohort=cohort,
        reference_panel=reference_panel,
        eqtl_model=eqtl_model,
        lv_code=lv_code,
        lv_percentile=lv_percentile,
        genes_symbols_dir=genes_symbols_dir,
        output_dir=output_dir,
        project_dir=project_dir,
    )

    # Execute the command using runner.invoke
    result = runner.invoke(cli.app, command)
    success = result.exit_code == 0
    message = result.stdout
    return success, message
