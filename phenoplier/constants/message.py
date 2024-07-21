from enum import StrEnum


class RegressionError(StrEnum):
    NO_GENE_NAME_COLUMN = "Mandatory columns not present in data 'gene_name'"
    NO_P_VALUE_COLUMN = "Mandatory columns not present in data 'p_value'"

class RegressionInfo(StrEnum):
    LOADING_INPUT = "Loading input data..."
