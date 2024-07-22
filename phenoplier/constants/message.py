from enum import StrEnum

# Todo: remove message prefix after print_and_log function is implemented
class RegressionError(StrEnum):
    NO_GENE_NAME_COLUMN = "ERROR: Mandatory columns not present in data 'gene_name'"
    NO_P_VALUE_COLUMN = "ERROR: Mandatory columns not present in data 'p_value'"
    DUP_GENES_FOUND = "ERROR: Duplicated genes in input data. Use option --dup-gene-action if you want to skip them."
    EXPECT_NO_GENE_CORR_FILE = "ERROR: When using '--model=ols', option '--gene-corr-file <value>' should not be provided."
    EXPECT_GENE_CORR_FILE = "ERROR: When using --model=gls, option '--gene-corr-file <value>' must be provided."
    INCOMPATIBLE_BATCH_ID_AND_LV_LIST = "ERROR: Incompatible parameters: LV list and batches cannot be used together"
    EXPECT_BOTH_BATCH_ARGS = "ERROR: Both --batch-id and --batch-n-splits have to be provided (not only one of them)"
    EXPECT_BATCH_ID_GT_ZERO = "ERROR: --batch-id must be >= 1"
    INCOMPATIBLE_BATCH_ARGS = "ERROR: --batch-id must be <= --batch-n-splits"
    EXPECT_BATCH_N_SPLITS_LT_LVS = "ERROR: --batch-n-splits cannot be greater than te number LVs in the model"

class RegressionInfo(StrEnum):
    LOADING_INPUT = "INFO: Loading input data..."
