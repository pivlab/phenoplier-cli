"""
This module contains enums used by the CLI commands.
"""

from enum import Enum, StrEnum


class Cohort(StrEnum):
    _1000g_eur = "1000g_eur"
    phenomexcan_rapid_gwas = "phenomexcan_rapid_gwas"
    phenomexcan_astle = "phenomexcan_astle"
    phenomexcan_other = "phenomexcan_other"


class RefPanel(StrEnum):
    _1000g = "1000G"
    gtex_v8 = "GTEX_V8"


class EqtlModel(StrEnum):
    mashr = "MASHR"
    elastic_net = "ELASTIC_NET"


class MatrixDtype(StrEnum):
    f32 = "float32"
    f64 = "float64"


class CovarOptions(Enum):
    ALL = "all"
    DEFAULT = "gene_size gene_size_log gene_density gene_density_log"
    GENE_SIZE = "gene_size"
    GENE_SIZE_LOG = "gene_size_log"
    GENE_DENSITY = "gene_density"
    GENE_DENSITY_LOG = "gene_density_log"
    GENE_N_SNPS_USED = "gene_n_snps_used"
    GENE_N_SNPS_USED_LOG = "gene_n_snps_used_log"
    GENE_N_SNPS_USED_DENSITY = "gene_n_snps_used_density"
    GENE_N_SNPS_USED_DENSITY_LOG = "gene_n_snps_used_density_log"


class DownloadAction(str, Enum):
    test_data = "test_data"
    ci_test_data = "ci_test_data"  # minimal set of data to be used in GitHub Action
    unit_test_data = "unit_test_data"
    full_data = "full_data"
    demo_data = "demo_data"
    smul_data = "smul_data"
    t21_data = "t21_data"
    nullsim_twas = "nullsim_twas"