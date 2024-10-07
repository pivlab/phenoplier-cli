import re
from plink import build_plink_nullsim_command, generate_pheno_names

# Existing tests for trim_spaces and remove_newline...

def test_generate_pheno_names():
    assert generate_pheno_names(1, 3) == "pheno1,pheno2,pheno3"
    assert generate_pheno_names(5, 7) == "pheno5,pheno6,pheno7"
    assert generate_pheno_names(1, 1) == "pheno1"
    assert generate_pheno_names(10, 10) == "pheno10"
    assert generate_pheno_names(1, 0) == ""


def test_build_plink_nullsim_command():
    # Test with minimal required arguments
    minimal_command = build_plink_nullsim_command(
        bgen_filename="test.bgen",
        covar="test_covar.txt",
        pheno="test_pheno.txt",
        pheno_name="test_pheno",
        sample="test_sample.txt"
    )
    assert "plink2" in minimal_command
    assert "--bgen test.bgen" in minimal_command
    assert "--covar test_covar.txt" in minimal_command
    assert "--pheno test_pheno.txt" in minimal_command
    assert "--pheno-name test_pheno" in minimal_command
    assert "--sample test_sample.txt" in minimal_command
    assert "--threads $(nproc --all)" in minimal_command

    # Test with custom arguments
    custom_command = build_plink_nullsim_command(
        bgen_filename="custom.bgen",
        covar="custom_covar.txt",
        covar_name="custom_covar1,custom_covar2",
        mac=100,
        maf=0.05,
        pheno="custom_pheno.txt",
        pheno_name="custom_pheno",
        sample="custom_sample.txt"
    )
    assert "--bgen custom.bgen" in custom_command
    assert "--covar custom_covar.txt" in custom_command
    assert "--covar-name custom_covar1,custom_covar2" in custom_command
    assert "--mac 100" in custom_command
    assert "--maf 0.05" in custom_command
    assert "--pheno custom_pheno.txt" in custom_command
    assert "--pheno-name custom_pheno" in custom_command
    assert "--sample custom_sample.txt" in custom_command

    # Verify that the command is a single line without extra spaces
    assert "\n" not in custom_command
    assert "  " not in custom_command

# To run the tests, use: pytest -v test_plink_commands.py