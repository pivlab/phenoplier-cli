from enum import StrEnum


class RegressionError(StrEnum):
    NO_GENE_NAME_COLUMN = "Mandatory columns not present in data 'gene_name'"


class RegressionInfo(StrEnum):
    LOADING_INPUT = "Loading input data..."
