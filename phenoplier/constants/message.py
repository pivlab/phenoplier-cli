from enum import StrEnum


class RegressionError(StrEnum):
    NO_GENE_NAME_COLUMN = "Mandatory columns not present in data 'gene_name'"
    NO_P_VALUE_COLUMN = "Mandatory columns not present in data 'p_value'"
    DUP_GENES_FOUND = "Duplicated genes in input data. Use option --dup-gene-action if you want to skip them."
    EXPECT_NO_GENE_CORR_FILE = "When using '--model=ols', option '--gene-corr-file <value>' should not be provided."
    EXPECT_GENE_CORR_FILE = "When using --model=gls, option '--gene-corr-file <value>' must be provided."

class RegressionInfo(StrEnum):
    LOADING_INPUT = "Loading input data..."
