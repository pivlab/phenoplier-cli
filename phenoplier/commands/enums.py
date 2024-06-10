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