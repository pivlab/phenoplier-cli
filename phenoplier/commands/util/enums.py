"""
This module contains enums used by the CLI commands.
"""

from enum import Enum


class Cohort(str, Enum):
    _1000g_eur = "1000g_eur"
    phenomexcan_rapid_gwas = "phenomexcan_rapid_gwas"
    phenomexcan_astle = "phenomexcan_astle"
    phenomexcan_other = "phenomexcan_other"


class RefPanel(str, Enum):
    _1000g = "1000G"
    gtex_v8 = "GTEX_V8"


class EqtlModel(str, Enum):
    mashr = "MASHR"
    elastic_net = "ELASTIC_NET"


class MatrixDtype(str, Enum):
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