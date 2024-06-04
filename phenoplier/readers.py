"""
Specifies functions to read different files used in the project.
"""
from pathlib import Path
import pandas as pd
from phenoplier.config import settings as conf


#
# Generic reader
#
def read_pickle(file_path: str, **kwargs):
    """
    Returns functions to read any python object stored as a pickle file

    Args:
        file_path: file path to be loaded.
        **kwargs: any other argument given to pandas.read_pickle

    Returns:

    """
    return lambda: pd.read_pickle(file_path, **kwargs)


def read_tsv(file_path: str, **kwargs):
    """
    Return functions to read any tab-separated text data file.

    Args:
        file_path: file path to be loaded.
        **kwargs: any other argument given to pandas.read_csv

    Returns:
        A function that reads file_path and, when run, returns a pandas
        DataFrame.
    """
    kwargs.pop("sep", None)

    return lambda: pd.read_csv(
        file_path,
        sep="\t",
        **kwargs,
    )


#
# General data
#
def read_term_id_xrefs():
    return pd.read_csv(
        conf.GENERAL["TERM_ID_XREFS_FILE"],
        sep="\t",
        index_col="term_id",
        dtype="category",
    )


#
# Phenotypes metadata
#
def read_phenomexcan_rapid_gwas_pheno_info_file():
    return pd.read_csv(
        conf.TWAS["RAPID_GWAS_PHENO_INFO_FILE"],
        sep="\t",
        index_col="phenotype",
    )


def read_phenomexcan_rapid_gwas_data_dict():
    return pd.read_csv(
        conf.TWAS["RAPID_GWAS_DATA_DICT_FILE"],
        sep="\t",
        index_col="FieldID",
    )


def read_phenomexcan_gtex_gwas_pheno_info():
    return pd.read_csv(
        conf.TWAS["GTEX_GWAS_PHENO_INFO_FILE"], sep="\t", index_col="Tag"
    )


#
# UK Biobank codings files
#
def read_uk_biobank_codings(coding_number):
    """Returns functions to read coding files for UK Biobank fields.

    Differently than the other read_* functions, this one returns functions instead
    of data.
    """
    return lambda: pd.read_csv(
        conf.UK_BIOBANK[f"CODING_{coding_number}_FILE"], sep="\t"
    )


#
# Genes
#
def read_genes_biomart_data():
    return pd.read_csv(
        conf.GENERAL["BIOMART_GENES_INFO_FILE"], index_col="ensembl_gene_id"
    )


def get_data_readers():
    #
    # This dictionary specifies as the value the function that knows how to read the
    # file given in the key.
    #
    data_readers = {
        # General
        conf.GENERAL["BIOMART_GENES_INFO_FILE"]: read_genes_biomart_data,
        conf.GENERAL["TERM_ID_XREFS_FILE"]: read_term_id_xrefs,
        # UK Biobank
        conf.UK_BIOBANK["CODING_3_FILE"]: read_uk_biobank_codings(3),
        conf.UK_BIOBANK["CODING_6_FILE"]: read_uk_biobank_codings(6),
        # TWAS
        conf.TWAS["RAPID_GWAS_PHENO_INFO_FILE"]: read_phenomexcan_rapid_gwas_pheno_info_file,
        conf.TWAS["RAPID_GWAS_DATA_DICT_FILE"]: read_phenomexcan_rapid_gwas_data_dict,
        conf.TWAS["GTEX_GWAS_PHENO_INFO_FILE"]: read_phenomexcan_gtex_gwas_pheno_info,
    }
    # Use map to apply Path to each key and construct the new dictionary
    data_readers = {Path(k): v for k, v in data_readers.items()}
    return data_readers


def get_data_format_readers():
    #
    # Differently than DATA_READERS, this dictionary does not specify absolute file
    # paths, but just extensions. It's useful when reading standard format such as
    # pickle.
    #
    return {
        ".pkl": read_pickle,
        ".tsv": read_tsv,
        ".tsv.gz": read_tsv,
    }
    return DATA_FORMAT_READERS