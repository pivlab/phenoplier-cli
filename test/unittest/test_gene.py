import pandas as pd
import pytest
import numpy as np

from phenoplier.entity import Gene


@pytest.mark.parametrize(
    "gene_property,gene_value",
    [("ensembl_id", "id_does_not_exist"), ("name", "name_does_not_exist")],
)
def test_gene_does_not_exist(gene_property, gene_value):
    with pytest.raises(ValueError):
        Gene(**{gene_property: gene_value})


@pytest.mark.parametrize(
    "gene_id,gene_name,gene_band",
    [
        ("ENSG00000003249", "DBNDD1", "16q24.3"),
        ("ENSG00000101440", "ASIP", "20q11.22"),
    ],
)
def test_gene_obj_from_gene_id(gene_id, gene_name, gene_band):
    gene = Gene(ensembl_id=gene_id)
    assert gene is not None
    assert gene.ensembl_id == gene_id
    assert gene.name == gene_name
    assert gene.band == gene_band

    gene = Gene(name=gene_name)
    assert gene is not None
    assert gene.ensembl_id == gene_id
    assert gene.name == gene_name
    assert gene.band == gene_band


@pytest.mark.parametrize(
    "gene_id,gene_name,gene_chr",
    [
        ("ENSG00000003249", "DBNDD1", "16"),
        ("ENSG00000101440", "ASIP", "20"),
    ],
)
def test_gene_obj_chromosome(gene_id, gene_name, gene_chr):
    gene = Gene(ensembl_id=gene_id)
    assert gene is not None
    assert gene.ensembl_id == gene_id
    assert gene.name == gene_name
    assert gene.chromosome == gene_chr

    gene = Gene(name=gene_name)
    assert gene is not None
    assert gene.ensembl_id == gene_id
    assert gene.name == gene_name
    assert gene.chromosome == gene_chr


@pytest.mark.parametrize(
    "tissue",
    [
        "Whole_Blood",
        "Testis",
    ],
)
def test_gene_get_tissue_connection(tissue):
    con = Gene._get_tissue_connection(tissue, model_type="MASHR")
    df = pd.read_sql(sql="select * from weights", con=con)
    assert df is not None
    assert df.shape[0] > 100
    assert df.shape[1] > 3


def test_gene_get_tissue_connection_tissue_does_not_exist():
    with pytest.raises(ValueError) as e:
        Gene._get_tissue_connection("NonExistent", model_type="MASHR")


@pytest.mark.parametrize(
    "gene_id,tissue,expected_snps_weights",
    [
        (
            "ENSG00000003249",
            "Whole_Blood",
            {
                "chr16_89979578_A_G_b38": 0.341560385316961,
                "chr16_90013161_G_C_b38": 0.493600048074392,
            },
        ),
        (
            "ENSG00000003249",
            "Testis",
            {
                "chr16_90015252_A_G_b38": 0.24632078046807,
            },
        ),
    ],
)
def test_gene_get_prediction_weights(gene_id, tissue, expected_snps_weights):
    w = Gene(ensembl_id=gene_id).get_prediction_weights(tissue, model_type="MASHR")
    assert w is not None
    assert w.shape[0] == len(expected_snps_weights)

    for snp_id, snp_weight in expected_snps_weights.items():
        assert w.loc[snp_id].round(5) == round(snp_weight, 5)


def test_gene_get_prediction_weights_empty():
    w = Gene(ensembl_id="ENSG00000183087").get_prediction_weights(
        "Whole_Blood", model_type="MASHR"
    )
    assert w is None


@pytest.mark.parametrize(
    "gene_pair,expected_snps1,expected_snps2,tissue",
    [
        (
            [
                "ENSG00000123200",
                "ENSG00000122026",
            ],
            [
                "chr13_46050849_T_C_b38",
                "chr13_46052725_T_C_b38",
            ],
            [
                "chr13_27242863_T_C_b38",
            ],
            "Whole_Blood",
        ),
        (
            [
                "ENSG00000123200",
                "ENSG00000122026",
            ],
            [
                "chr13_46029707_C_T_b38",
            ],
            [
                "chr13_27251616_G_C_b38",
                "chr13_27252069_G_A_b38",
            ],
            "Adipose_Subcutaneous",
        ),
    ],
)
def test_gene_get_snps_cov_genes_same_chromosome(
    gene_pair, expected_snps1, expected_snps2, tissue
):
    g1 = Gene(ensembl_id=gene_pair[0])
    g2 = Gene(ensembl_id=gene_pair[1])

    g1_snps = g1.get_prediction_weights(tissue, model_type="MASHR").index
    g2_snps = g2.get_prediction_weights(tissue, model_type="MASHR").index

    df, g1_snps_info, g2_snps_info = Gene._get_snps_cov(g1_snps, g2_snps)
    assert df is not None
    assert df.shape[0] == g1_snps.shape[0] == len(expected_snps1)
    assert df.shape[1] == g2_snps.shape[0] == len(expected_snps2)
    assert not np.isnan(df).any()
    assert g1_snps_info[0] == expected_snps1
    assert g2_snps_info[0] == expected_snps2


@pytest.mark.parametrize(
    "gene_pair,expected_snps1,expected_snps2,tissue",
    [
        (
            [
                "ENSG00000166821",
                "ENSG00000140545",
            ],
            [
                "chr15_89690738_G_C_b38",
            ],
            [
                "chr15_88913717_G_A_b38",
                "chr15_88917324_A_G_b38",
                # "chr15_88945286_AAAGTGCTGAGATCCTCCTACCTCT_A_b38", this one is not present in 1000G
            ],
            "Whole_Blood",
        ),
    ],
)
def test_gene_get_snps_cov_genes_same_chromosome_some_snps_missing_cov(
    gene_pair, expected_snps1, expected_snps2, tissue
):
    g1 = Gene(ensembl_id=gene_pair[0])
    g2 = Gene(ensembl_id=gene_pair[1])

    g1_snps = g1.get_prediction_weights(tissue, model_type="MASHR").index
    g2_snps = g2.get_prediction_weights(tissue, model_type="MASHR").index

    df, g1_snps_info, g2_snps_info = Gene._get_snps_cov(
        g1_snps, g2_snps, reference_panel="1000g"
    )
    assert df is not None
    assert df.shape[0] == len(expected_snps1)
    assert df.shape[1] == len(expected_snps2)
    assert (len(g1_snps) > len(expected_snps1)) or (len(g2_snps) > len(expected_snps2))
    assert not np.isnan(df).any()
    assert g1_snps_info[0] == expected_snps1
    assert g2_snps_info[0] == expected_snps2


@pytest.mark.parametrize(
    "gene_pair,expected_snps1,tissue",
    [
        (
            [
                "ENSG00000123200",
            ],
            [
                "chr13_46050849_T_C_b38",
                "chr13_46052725_T_C_b38",
            ],
            "Whole_Blood",
        ),
        (
            [
                "ENSG00000122026",
            ],
            [
                "chr13_27251616_G_C_b38",
                "chr13_27252069_G_A_b38",
            ],
            "Adipose_Subcutaneous",
        ),
    ],
)
def test_gene_get_snps_cov_one_gene(gene_pair, expected_snps1, tissue):
    g1 = Gene(ensembl_id=gene_pair[0])

    g1_snps = g1.get_prediction_weights(tissue, model_type="MASHR").index

    df, g1_snps_info, g2_snps_info = Gene._get_snps_cov(g1_snps)
    assert df is not None
    assert g1_snps_info == g2_snps_info
    assert df.shape[0] == df.shape[1] == g1_snps.shape[0] == len(expected_snps1)
    assert not np.isnan(df).any()
    assert g1_snps_info[0] == expected_snps1


def test_gene_get_snps_cov_snp_list_different_chromosomes():
    g1_snps = [
        "chr13_45120003_C_T_b38",
        "chr13_49493306_T_C_b38",
        "chr12_25064415_T_C_b38",
    ]

    with pytest.raises(ValueError) as e:
        Gene._get_snps_cov(g1_snps, check=True)


def test_gene_get_snps_cov_genes_different_chromosomes():
    tissue = "Whole_Blood"

    g1 = Gene(ensembl_id="ENSG00000123200")
    g2 = Gene(ensembl_id="ENSG00000133065")

    g1_snps = g1.get_prediction_weights(tissue, model_type="MASHR").index
    g2_snps = g2.get_prediction_weights(tissue, model_type="MASHR").index

    with pytest.raises(Exception) as e:
        Gene._get_snps_cov(g1_snps, g2_snps, check=True)


@pytest.mark.parametrize(
    "gene_id,tissue,expected_var",
    [
        (
            "ENSG00000157227",
            "Whole_Blood",
            0.001,
        ),
        (
            "ENSG00000157227",
            "Testis",
            0.0001,
        ),
        (
            "ENSG00000096696",
            "Adipose_Subcutaneous",
            0.0712,
        ),
        (
            "ENSG00000096696",
            "Colon_Transverse",
            0.0002,
        ),
    ],
)
def test_gene_get_pred_expression_variance(gene_id, tissue, expected_var):
    g = Gene(ensembl_id=gene_id)
    g_var = g.get_pred_expression_variance(
        tissue, reference_panel="1000G", model_type="MASHR"
    )
    assert g_var is not None
    assert isinstance(g_var, float)

    assert round(g_var, 4) == round(expected_var, 4)


def test_gene_get_pred_expression_variance_gene_not_in_tissue():
    g = Gene(ensembl_id="ENSG00000183087")
    g_var = g.get_pred_expression_variance(
        "Brain_Cerebellar_Hemisphere", reference_panel="1000g", model_type="MASHR"
    )
    assert g_var is None


@pytest.mark.parametrize(
    "gene_id1,gene_id2,tissue,expected_corr",
    [
        # case where some snps in the second gene are not in covariance snp matrix
        (
            "ENSG00000166821",
            "ENSG00000140545",
            "Whole_Blood",
            0.0477,
        ),
        # case where all snps are in cov matrix
        (
            "ENSG00000121101",
            "ENSG00000169750",
            "Brain_Cortex",
            0.05,
        ),
        # case of highly correlated genes
        (
            "ENSG00000134871",
            "ENSG00000187498",
            "Whole_Blood",
            0.9702,
        ),
        # corr of genes from different chromosomes is always zero
        # (same gene pair across different tissues)
        ("ENSG00000166821", "ENSG00000121101", "Whole_Blood", 0.00),
        ("ENSG00000166821", "ENSG00000121101", "Brain_Cortex", 0.00),
        ("ENSG00000166821", "ENSG00000121101", "Brain_Spinal_cord_cervical_c-1", 0.00),
        # corr of genes from different chromosomes is always zero
        ("ENSG00000134871", "ENSG00000169750", "Whole_Blood", 0.00),
        ("ENSG00000134871", "ENSG00000169750", "Brain_Cortex", 0.00),
        ("ENSG00000134871", "ENSG00000169750", "Testis", 0.00),
    ],
)
def test_gene_get_expression_correlation_in_same_tissues(
    gene_id1, gene_id2, tissue, expected_corr
):
    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    genes_corr = gene1.get_expression_correlation(
        gene2, tissue, reference_panel="1000g", use_within_distance=False
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert 0.0 <= genes_corr <= 1.0

    # correlation should be asymmetric
    genes_corr_2 = gene2.get_expression_correlation(
        gene1, tissue, reference_panel="1000g", use_within_distance=False
    )
    assert round(genes_corr_2, 4) == round(genes_corr, 4)

    # correlation with itself should be 1.0
    assert (
        round(
            gene1.get_expression_correlation(
                gene1, tissue, reference_panel="1000g", use_within_distance=False
            ),
            4,
        )
        == 1.0
    )
    assert (
        round(
            gene2.get_expression_correlation(
                gene2, tissue, reference_panel="1000g", use_within_distance=False
            ),
            4,
        )
        == 1.0
    )

    assert round(genes_corr, 4) == round(expected_corr, 4)


@pytest.mark.parametrize(
    "gene1_id,gene1_tissue,gene2_id,gene2_tissue,expected_corr",
    [
        # case where some snps in the second gene are not in covariance snp matrix
        (
            "ENSG00000166821",
            "Whole_Blood",
            "ENSG00000140545",
            "Liver",
            -0.03596169385766873,
        ),
        # case where all snps are in cov matrix
        (
            "ENSG00000121101",
            "Artery_Coronary",
            "ENSG00000169750",
            "Stomach",
            -0.0794586198132903,
        ),
        # case of highly correlated genes
        (
            "ENSG00000134871",
            "Artery_Coronary",
            "ENSG00000187498",
            "Artery_Aorta",
            0.9301565975324726,
        ),
    ],
)
def test_gene_get_expression_correlation_in_different_tissues(
    gene1_id, gene1_tissue, gene2_id, gene2_tissue, expected_corr
):
    gene1 = Gene(ensembl_id=gene1_id)
    gene2 = Gene(ensembl_id=gene2_id)

    genes_corr = gene1.get_expression_correlation(
        tissue=gene1_tissue,
        other_gene=gene2,
        other_tissue=gene2_tissue,
        reference_panel="1000g",
        use_within_distance=False,
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(expected_corr, rel=1e-5)

    # correlation should be asymmetric
    genes_corr_2 = gene2.get_expression_correlation(
        tissue=gene2_tissue,
        other_gene=gene1,
        other_tissue=gene1_tissue,
        reference_panel="1000g",
        use_within_distance=False,
    )
    assert genes_corr_2 == pytest.approx(genes_corr, rel=10e-10)


@pytest.mark.parametrize(
    # the expression of all these genes is the real one, and was calculated
    # using the script tests/test_cases/predict_gene_expression.py
    "gene_id1,gene_id2,tissue,expected_corr",
    [
        # case where all snps are in cov matrix
        (
            "ENSG00000169750",
            "ENSG00000121101",
            "Brain_Cortex",
            0.05004568731277303,
        ),
        # case where some snps in the second gene are not in covariance snp matrix
        (
            "ENSG00000166821",
            "ENSG00000140545",
            "Whole_Blood",
            0.04774750700416392,
        ),
        # case of highly correlated genes
        (
            "ENSG00000134871",
            "ENSG00000187498",
            "Whole_Blood",
            0.9702481569810856,
        ),
        # case of negative correlation
        (
            "ENSG00000000938",
            "ENSG00000004455",
            "Whole_Blood",
            -0.03605498187542936,
        ),
    ],
)
def test_gene_get_expression_correlation_compare_with_real_correlation(
    gene_id1, gene_id2, tissue, expected_corr
):
    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    genes_corr = gene1.get_expression_correlation(
        gene2, tissue, reference_panel="1000g", use_within_distance=False
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert np.isclose(genes_corr, expected_corr)


@pytest.mark.parametrize(
    # the expression of all these genes is the real one, and was calculated
    # using the script tests/test_cases/predict_gene_expression.py
    # in that script, I changed the gene0/gene1 dataframes by removing some
    # SNPs so they are not included when computing expression correlation
    "gene_id1,gene_id2,tissue,snps_subset,expected_corr",
    [
        # case where all snps are in cov matrix
        (
            "ENSG00000169750",
            "ENSG00000121101",
            "Brain_Cortex",
            {
                # first gene snps: all of them
                "chr17_82032100_A_T_b38",
                # second gene snps: remove chr17_58690513_G_A_b38
                "chr17_58695876_A_G_b38",
            },
            0.0709243871577751,
        ),
        # case where some snps in the second gene are not in covariance snp matrix
        (
            "ENSG00000166821",
            "ENSG00000140545",
            "Whole_Blood",
            {
                # first gene snps: all of them
                "chr15_89690738_G_C_b38",
                # second gene snps: chr15_88945286_AAAGTGCTGAGATCCTCCTACCTCT_A_b38 is not
                # in genotype data, and remove chr15_88913717_G_A_b38
                "chr15_88917324_A_G_b38",
            },
            0.07412638583307823,
        ),
        # case of highly correlated genes using all snps, but both genes have
        # only one snp; here I remove one of them, so the correlation should be
        # None/NaN
        (
            "ENSG00000134871",
            "ENSG00000187498",
            "Whole_Blood",
            {
                # first gene snps: all of them
                "chr13_110305525_T_G_b38",
                # second gene snps: remove the single one chr13_110307117_C_A_b38
            },
            None,
        ),
        # case of negative correlation
        (
            "ENSG00000000938",
            "ENSG00000004455",
            "Whole_Blood",
            {
                # first gene snps: all of them
                "chr1_27636786_T_C_b38",
                # second gene snps: only one of them
                "chr1_33071920_A_C_b38",
            },
            -0.01826437561866124,
        ),
    ],
)
def test_gene_get_expression_correlation_subset_of_snps(
    gene_id1, gene_id2, tissue, snps_subset, expected_corr
):
    # here snps_subset is supposed to be a set of SNPs present, for example,
    # in the GWASs, so only those must be taken into consideration to compute
    # correlation
    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    # snps_subset needs to be frozenset (for caching in entity.py)
    snps_subset = frozenset(snps_subset)

    genes_corr = gene1.get_expression_correlation(
        gene2,
        tissue,
        reference_panel="1000g",
        use_within_distance=False,
        snps_subset=snps_subset,
    )

    if expected_corr is None:
        assert genes_corr is None
    else:
        assert genes_corr is not None
        assert isinstance(genes_corr, float)
        assert genes_corr == pytest.approx(expected_corr, rel=1e-5)


@pytest.mark.parametrize(
    "gene_id1,gene_id2,tissue,expected_corr",
    [
        # case where there is no model for a gene in that tissue
        # here ENSG00000166821 has no snps in Ovary
        ("ENSG00000166821", "ENSG00000121101", "Ovary", 0.00),
        # case where snps for one gene are not in snp cov matrix
        # here ENSG00000163221 has one predictor snp, but it is not in cov
        # matrix
        ("ENSG00000134686", "ENSG00000163221", "Brain_Cerebellar_Hemisphere", 0.00),
    ],
)
def test_gene_get_expression_correlation_no_prediction_models(
    gene_id1, gene_id2, tissue, expected_corr
):
    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    genes_corr = gene1.get_expression_correlation(
        gene2, tissue, reference_panel="1000g"
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert 0.0 <= genes_corr <= 1.0

    # correlation should be asymmetric
    genes_corr_2 = gene2.get_expression_correlation(
        gene1, tissue, reference_panel="1000g"
    )
    assert genes_corr_2 == genes_corr

    assert genes_corr == expected_corr


def test_gene_get_expression_correlation_gene_weights_are_zero():
    gene1 = Gene(ensembl_id="ENSG00000134686")

    # weights for this gene in whole blood are all zero
    gene2 = Gene(ensembl_id="ENSG00000117215")

    tissue = "Whole_Blood"

    genes_corr = gene1.get_expression_correlation(
        gene2, tissue, reference_panel="1000g"
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 0.0


def test_get_tissues_correlations_same_gene():
    # ENSG00000122025
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(
        gene1, reference_panel="1000G", model_type="MASHR"
    )

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (41, 41)
    genes_corrs_diag_unique_values = np.unique(np.diag(genes_corrs))
    assert genes_corrs_diag_unique_values.shape[0] == 1
    assert genes_corrs_diag_unique_values[0] == 1.0
    np.testing.assert_array_almost_equal(genes_corrs, genes_corrs.T)

    # check some values precomputed using tests/test_cases/predict_gene_expression.py
    # all values for Kidney_Cortex are zero
    assert "Kidney_Cortex" not in genes_corrs.index
    assert genes_corrs.loc[
        "Skin_Not_Sun_Exposed_Suprapubic", "Spleen"
    ] == pytest.approx(0.9730644425264104, rel=1e-5)
    assert genes_corrs.loc[
        "Brain_Substantia_nigra", "Skin_Not_Sun_Exposed_Suprapubic"
    ] == pytest.approx(-0.07524348080571082, rel=1e-5)


def test_get_tissues_correlations_different_gene():
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")

    # MARCKSL1
    # chr 1
    gene2 = Gene(ensembl_id="ENSG00000175130")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(gene2)

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (49, 49)
    genes_corrs_diag_unique_values = np.unique(np.diag(genes_corrs))
    assert genes_corrs_diag_unique_values.shape[0] == 1
    assert genes_corrs_diag_unique_values[0] == 0.0

    genes_corrs_unique_values = genes_corrs.unstack().unique()
    assert genes_corrs_unique_values.shape[0] == 1
    assert genes_corrs_unique_values[0] == 0.0


def test_get_tissues_correlations_subset_of_tissues_single_same_tissue_both_genes():
    # COL4A2 - 13q34
    gene1 = Gene(ensembl_id="ENSG00000134871")

    # COL4A1 - 13q34
    gene2 = Gene(ensembl_id="ENSG00000187498")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(
        gene2,
        reference_panel="1000G",
        tissues=("Whole_Blood",),
        other_tissues=("Whole_Blood",),
    )

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (1, 1)
    assert genes_corrs.iloc[0, 0] == pytest.approx(0.9702481569810856, rel=1e-5)


def test_get_tissues_correlations_subset_of_tissues_several_tissues():
    # COL4A2 - 13q34
    gene1 = Gene(ensembl_id="ENSG00000134871")

    # COL4A1 - 13q34
    gene2 = Gene(ensembl_id="ENSG00000187498")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(
        other_gene=gene2,
        tissues=("Whole_Blood", "Artery_Coronary"),
        other_tissues=("Artery_Aorta", "Whole_Blood", "Ovary"),
        reference_panel="1000G",
    )

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (2, 3)
    assert genes_corrs.loc["Whole_Blood", "Artery_Aorta"] == pytest.approx(
        -0.9301565975324703, rel=1e-5
    )
    assert genes_corrs.loc["Whole_Blood", "Whole_Blood"] == pytest.approx(
        0.9702481569810856, rel=1e-5
    )
    assert genes_corrs.loc["Whole_Blood", "Ovary"] == pytest.approx(
        -0.9702481569810807, rel=1e-5
    )
    assert genes_corrs.loc["Artery_Coronary", "Artery_Aorta"] == pytest.approx(
        0.9301565975324726, rel=1e-5
    )
    assert genes_corrs.loc["Artery_Coronary", "Whole_Blood"] == pytest.approx(
        -0.9702481569810858, rel=1e-5
    )
    assert genes_corrs.loc["Artery_Coronary", "Ovary"] == pytest.approx(
        0.9702481569810842, rel=1e-5
    )


def test_get_tissues_correlations_gene_without_prediction_models():
    # WNT10A - 2q35
    gene1 = Gene(ensembl_id="ENSG00000135925")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(gene1)

    # check shape
    assert genes_corrs is None


def test_get_tissues_covariances_same_gene():
    # ENSG00000122025
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")
    gene1_tissues = ("Small_Intestine_Terminal_Ileum", "Uterus")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(
        gene1,
        tissues=gene1_tissues,
        other_tissues=gene1_tissues,
        reference_panel="1000G",
        model_type="MASHR",
        return_covariance=True,
    )

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (2, 2)
    np.testing.assert_array_almost_equal(genes_corrs, genes_corrs.T)

    expected_genes_cov = np.array(
        [[1.98515754e-02, -4.47984702e-05], [-4.47984702e-05, 1.88315869e-05]]
    )

    np.testing.assert_array_almost_equal(genes_corrs, expected_genes_cov)


def test_get_tissues_covariances_different_gene():
    gene1 = Gene(ensembl_id="ENSG00000180596")
    gene1_tissues = ("Small_Intestine_Terminal_Ileum", "Uterus")

    gene2 = Gene(ensembl_id="ENSG00000180573")
    gene2_tissues = ("Nerve_Tibial", "Lung", "Testis")

    # get the correlation matrix of the gene expression across all tissues
    genes_corrs = gene1.get_tissues_correlations(
        gene2,
        tissues=gene1_tissues,
        other_tissues=gene2_tissues,
        reference_panel="1000G",
        model_type="MASHR",
        return_covariance=True,
    )

    # check shape
    assert genes_corrs is not None
    assert not genes_corrs.isna().any().any()
    assert genes_corrs.shape == (2, 3)

    expected_genes_cov = np.array(
        [
            [-6.37965457e-05, -4.96063897e-05, 1.27066555e-04],
            [-6.97638808e-05, 6.98772264e-05, -6.23564904e-04],
        ]
    )
    np.testing.assert_array_almost_equal(genes_corrs, expected_genes_cov)


def test_get_tissues_correlations_svd_two_tissues():
    gene1 = Gene(ensembl_id="ENSG00000010256")
    gene1_tissues = ("Thyroid", "Whole_Blood")

    u, s, vt = gene1.get_tissues_correlations_svd(
        tissues=gene1_tissues,
        reference_panel="1000G",
        model_type="MASHR",
    )

    np.testing.assert_array_almost_equal(
        u, np.array([[-0.70710678, 0.70710678], [0.70710678, 0.70710678]])
    )

    np.testing.assert_array_almost_equal(s, np.array([1.00936897, 0.99063103]))

    np.testing.assert_array_almost_equal(
        vt, np.array([[-0.70710678, 0.70710678], [0.70710678, 0.70710678]])
    )


def test_get_tissues_correlations_svd_five_tissues():
    gene1 = Gene(ensembl_id="ENSG00000009709")
    gene1_tissues = (
        "Brain_Amygdala",
        "Brain_Cortex",
        "Brain_Substantia_nigra",
        "Muscle_Skeletal",
        "Pituitary",
    )

    u, s, vt = gene1.get_tissues_correlations_svd(
        tissues=gene1_tissues,
        reference_panel="1000G",
        model_type="MASHR",
    )

    np.testing.assert_array_almost_equal(
        u,
        np.array(
            [
                [-0.49909521, -0.03006604],
                [0.06013209, -0.99819043],
                [-0.49909521, -0.03006604],
                [-0.49909521, -0.03006604],
                [-0.49909521, -0.03006604],
            ]
        ),
    )

    np.testing.assert_array_almost_equal(s, np.array([4.01092662, 0.98907338]))

    np.testing.assert_array_almost_equal(
        vt,
        np.array(
            [
                [-0.49909521, 0.06013209, -0.49909521, -0.49909521, -0.49909521],
                [-0.03006604, -0.99819043, -0.03006604, -0.03006604, -0.03006604],
            ]
        ),
    )


def test_get_tissues_covariances_svd_two_tissues():
    gene1 = Gene(ensembl_id="ENSG00000010256")
    gene1_tissues = ("Thyroid", "Whole_Blood")

    u, s, vt = gene1.get_tissues_correlations_svd(
        tissues=gene1_tissues,
        reference_panel="1000G",
        model_type="MASHR",
        use_covariance_matrix=True,
    )

    np.testing.assert_array_almost_equal(
        u, np.array([[-0.9999842, 0.0056221], [0.0056221, 0.9999842]])
    )

    np.testing.assert_array_almost_equal(s, np.array([0.00092732, 0.00020345]))

    np.testing.assert_array_almost_equal(
        vt, np.array([[-0.9999842, 0.0056221], [0.0056221, 0.9999842]])
    )


def test_get_tissues_covariances_svd_five_tissues():
    gene1 = Gene(ensembl_id="ENSG00000009709")
    gene1_tissues = (
        "Brain_Amygdala",
        "Brain_Cortex",
        "Brain_Substantia_nigra",
        "Muscle_Skeletal",
        "Pituitary",
    )

    u, s, vt = gene1.get_tissues_correlations_svd(
        tissues=gene1_tissues,
        reference_panel="1000G",
        model_type="MASHR",
        use_covariance_matrix=True,
    )

    np.testing.assert_array_almost_equal(
        u,
        np.array(
            [
                [-0.00248747],
                [0.99994296],
                [-0.00359127],
                [-0.00787331],
                [-0.00574532],
            ]
        ),
    )

    np.testing.assert_array_almost_equal(s, np.array([0.00299917]))

    np.testing.assert_array_almost_equal(
        vt,
        np.array(
            [
                [-0.00248747, 0.99994296, -0.00359127, -0.00787331, -0.00574532],
            ]
        ),
    )


@pytest.mark.parametrize(
    "gene_id1,gene_id2,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        # case with low correlation
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: -0.007504128812187361
        ("ENSG00000000938", "ENSG00000004455", 0.0063366557885307815),
        # case with moderate correlation
        #  NOC2L (1p36.33) and HES4 (1p36.33) - corr ssm: 0.09936675951373465
        ("ENSG00000188976", "ENSG00000188290", 0.11545923512363486),
        # case with high correlation
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.26949013268938227
        ("ENSG00000134871", "ENSG00000187498", 0.2741277581419143),
        # case in same chromosome but far away
        #  IRF4 (6p25.3) and TBP (6q27) - corr ssm: 0.021562228484490575
        ("ENSG00000137265", "ENSG00000112592", 0.005050971898013959),
        # case in same band, low correlation
        #  ARSA (22q13.33) and SHANK3 (22q13.33) - corr ssm: 0.04978481316292831
        ("ENSG00000100299", "ENSG00000251322", 0.03227259989743747),
        # case in same chromosome, close bands, moderate correlation
        #  IKZF3 (17q21.1) and PNMT (17q12) - corr ssm: 0.17760073544652036
        ("ENSG00000161405", "ENSG00000141744", 0.17247836072948008),
        # case in same band, very high correlation
        #  CCL2 (17q12) and CCL7 (17q12) - corr ssm: 0.6711777075122141
        ("ENSG00000108691", "ENSG00000108688", 0.6800818985116897),
        # case in same band, moderate correlation
        #  CCL2 (17q12) and CCL8 (17q12) - corr ssm: 0.18428851723519474
        ("ENSG00000108691", "ENSG00000108700", 0.19085429774422794),
        # case from LV, same chromosome, low correlation
        #  HIST2H2BF (1q21.2) and HIST3H2A (1q42.13) - corr ssm: -0.004591318762258967
        ("ENSG00000203814", "ENSG00000181218", 0.004857218553958475),
        # case from LV, same chromosome, low correlation
        #  HIST2H2BF (1q21.2) and HIST3H2BB (1q42.13) - corr ssm: -0.004810914232651819
        ("ENSG00000203814", "ENSG00000196890", 0.0033322198833564283),
        # case from LV, same band, high correlation
        #  HIST3H2A (1q42.13) and HIST3H2BB (1q42.13) - corr ssm: 0.4742359153016549
        ("ENSG00000181218", "ENSG00000196890", 0.4653524586237968),
        # case from LV, same band, very high correlation
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.866327373684711
        ("ENSG00000180596", "ENSG00000180573", 0.8681004435630797),
        # case from LV, same band, moderate correlation
        #  HIST1H2BO (6p22.1) and HIST1H2BK (6p22.1) - corr ssm: 0.16879943739503644
        ("ENSG00000274641", "ENSG00000197903", 0.17441877369957684),
        # case from LV, same chromosome, close bands, no correlation
        #  HIST1H2BO (6p22.1) and HIST1H2BF (6p22.2) - corr ssm: -0.008777382945963396
        ("ENSG00000274641", "ENSG00000277224", 0.008837131332243578),
    ],
)
def test_ssm_correlation_1000G_using_all_tissues(gene_id1, gene_id2, expected_corr):
    def compute_ssm_correlation(g1, g2):
        return g1.get_ssm_correlation(
            g2, reference_panel="1000G", model_type="MASHR", use_within_distance=False
        )

    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    genes_corr = compute_ssm_correlation(gene1, gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(expected_corr, rel=0.005)

    # check symmetry
    assert compute_ssm_correlation(gene2, gene1) == pytest.approx(genes_corr, rel=1e-10)


@pytest.mark.parametrize(
    "gene_id1,gene_id2,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        # case with low correlation
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.00983770332486997
        ("ENSG00000000938", "ENSG00000004455", 0.0021024381106464346),
        # case with moderate correlation
        #  NOC2L (1p36.33) and HES4 (1p36.33) - corr ssm: 0.11115599249803236
        ("ENSG00000188976", "ENSG00000188290", 0.11197048734672312),
        # case with high correlation
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.2765384240594094
        ("ENSG00000134871", "ENSG00000187498", 0.26083472608235997),
        # # case from LV, same band, very high correlation
        # #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.866327373684711
        # ("ENSG00000180596", "ENSG00000180573", 0.8681004435630797),
    ],
)
def test_ssm_correlation_GTEX_V8_using_all_tissues(gene_id1, gene_id2, expected_corr):
    def compute_ssm_correlation(g1, g2):
        return g1.get_ssm_correlation(
            g2, reference_panel="GTEX_V8", model_type="MASHR", use_within_distance=False
        )

    gene1 = Gene(ensembl_id=gene_id1)
    gene2 = Gene(ensembl_id=gene_id2)

    genes_corr = compute_ssm_correlation(gene1, gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(expected_corr, rel=0.005)

    # check symmetry
    assert compute_ssm_correlation(gene2, gene1) == pytest.approx(genes_corr, rel=1e-10)


@pytest.mark.parametrize(
    "gene1_id,gene1_tissues,gene2_id,gene2_tissues,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        #
        # case with low correlation, same subset of tissues
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.004334531855003577
        (
            "ENSG00000000938",
            ("Whole_Blood", "Liver"),
            "ENSG00000004455",
            ("Whole_Blood", "Liver"),
            0.0037750542776042078,
        ),
        # case with low/moderate correlation, same subset of tissues but different
        #  order
        #  NOC2L (1p36.33) and HES4 (1p36.33) - corr ssm: 0.031233667345898525
        (
            "ENSG00000188976",
            ("Vagina", "Colon_Sigmoid", "Adipose_Subcutaneous"),
            "ENSG00000188290",
            ("Adipose_Subcutaneous", "Vagina", "Colon_Sigmoid"),
            0.05105487507372672,
        ),
        # case with high correlation, only one tissue and the same one
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.9422694271657404
        (
            "ENSG00000134871",
            ("Whole_Blood",),
            "ENSG00000187498",
            ("Whole_Blood",),
            0.9450480122997846,
        ),
        # same case as before, with only one tissue but a different one
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.8592059297353322
        (
            "ENSG00000134871",
            ("Artery_Coronary",),
            "ENSG00000187498",
            ("Artery_Aorta",),
            0.8685610738386613,
        ),
        # same case as before, but with asymmetric number of distinct tissues
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.9240418273534601
        (
            "ENSG00000134871",
            ("Artery_Coronary", "Whole_Blood", "Pituitary", "Nerve_Tibial"),
            "ENSG00000187498",
            ("Testis", "Pancreas"),
            0.9267879969125328,
        ),
        # same case as before, but tissues exchanged (some do not exist for
        #  first gene)
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.656725901368496
        (
            "ENSG00000134871",
            ("Testis", "Pancreas"),  # no model for Pancreas
            "ENSG00000187498",
            ("Artery_Coronary", "Whole_Blood", "Pituitary", "Nerve_Tibial"),
            0.6625281614888511,
        ),
        # same case as before, but tissues exchanged (some do not exist for
        #  second gene)
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: -0.007060792745146127
        (
            "ENSG00000134871",
            ("Artery_Coronary", "Whole_Blood", "Pituitary", "Nerve_Tibial"),
            "ENSG00000187498",
            (
                "Adipose_Visceral_Omentum",
                "Brain_Amygdala",
            ),  # no model for Brain_Amygdala
            0.0014496394482319279,
        ),
        # case in same chromosome, close bands, moderate correlation
        #  IKZF3 (17q21.1) and PNMT (17q12) - corr ssm: 0.1790853137947722
        (
            "ENSG00000161405",
            ("Lung", "Muscle_Skeletal"),
            "ENSG00000141744",
            (
                "Prostate",
                "Small_Intestine_Terminal_Ileum",
                "Skin_Sun_Exposed_Lower_leg",
            ),
            0.19199621017966995,
        ),
    ],
)
def test_ssm_correlation_1000G_using_subsets_tissues(
    gene1_id, gene1_tissues, gene2_id, gene2_tissues, expected_corr
):
    def compute_ssm_correlation(g1, g1_tis, g2, g2_tis):
        return g1.get_ssm_correlation(
            other_gene=g2,
            tissues=g1_tis,
            other_tissues=g2_tis,
            reference_panel="1000G",
            model_type="MASHR",
            use_within_distance=False,
        )

    gene1 = Gene(ensembl_id=gene1_id)
    gene2 = Gene(ensembl_id=gene2_id)

    genes_corr = compute_ssm_correlation(gene1, gene1_tissues, gene2, gene2_tissues)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(expected_corr, rel=5e-3)

    # check symmetry
    assert compute_ssm_correlation(
        gene2, gene2_tissues, gene1, gene1_tissues
    ) == pytest.approx(genes_corr, rel=1e-10)


@pytest.mark.parametrize(
    "gene1_id,gene1_tissues,gene2_id,gene2_tissues,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        #
        # case with low correlation, same subset of tissues
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.00444960131880503
        (
            "ENSG00000000938",
            ("Whole_Blood", "Liver"),
            "ENSG00000004455",
            ("Whole_Blood", "Liver"),
            0.000542792546989301,
        ),
        # case with low/moderate correlation, same subset of tissues but different
        #  order
        #  NOC2L (1p36.33) and HES4 (1p36.33) - corr ssm: 0.041358374600804444
        (
            "ENSG00000188976",
            ("Vagina", "Colon_Sigmoid", "Adipose_Subcutaneous"),
            "ENSG00000188290",
            ("Adipose_Subcutaneous", "Vagina", "Colon_Sigmoid"),
            0.049725788022196515,
        ),
        # case with high correlation, only one tissue and the same one
        #  COL4A2 (13q34) and COL4A1 (13q34) - corr ssm: 0.9118241351150527
        (
            "ENSG00000134871",
            ("Whole_Blood",),
            "ENSG00000187498",
            ("Whole_Blood",),
            0.9193135210093487,
        ),
    ],
)
def test_ssm_correlation_GTEX_V8_using_subsets_tissues(
    gene1_id, gene1_tissues, gene2_id, gene2_tissues, expected_corr
):
    def compute_ssm_correlation(g1, g1_tis, g2, g2_tis):
        return g1.get_ssm_correlation(
            other_gene=g2,
            tissues=g1_tis,
            other_tissues=g2_tis,
            reference_panel="GTEX_V8",
            model_type="MASHR",
            use_within_distance=False,
        )

    gene1 = Gene(ensembl_id=gene1_id)
    gene2 = Gene(ensembl_id=gene2_id)

    genes_corr = compute_ssm_correlation(gene1, gene1_tissues, gene2, gene2_tissues)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(expected_corr, rel=5e-3)

    # check symmetry
    assert compute_ssm_correlation(
        gene2, gene2_tissues, gene1, gene1_tissues
    ) == pytest.approx(genes_corr, rel=1e-10)


@pytest.mark.parametrize(
    "gene1_id,gene1_tissues,gene2_id,gene2_tissues,snps_subset,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        #
        # case where all SNPs are used (at least 2 SNPs per gene per tissue)
        #  I use this case for comparison with other cases below
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: -0.003771674549162753
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            None,
            0.0019803784985639333,
        ),
        # exactly the same case, here I just specify all the SNPs manually (so
        #  it has to return the same correlation)
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: same as before
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            0.0019803784985639333,
        ),
        # same case, but some SNPs are removed in the first gene, first tissue
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: -0.004422420712027562
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                # "chr1_27634281_G_A_b38",  # remove the one with largest effect
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            0.0029427325584488006,
        ),
        # same case, but some SNPs are removed in the first gene, second tissue
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.0033504293601502692
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                # "chr1_27634321_C_G_b38", # remove
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            0.0009373552873566728,
        ),
        # same case, but some SNPs are removed in the second gene, first tissue
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: -0.010539889181369597
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                # "chr1_33080995_A_G_b38",  # remove
                #  Liver
                # "chr1_33080995_A_G_b38",  # (same as other one)
                "chr1_33085456_C_G_b38",
            },
            0.0021756612863551364,
        ),
        # same case, but some SNPs are removed in the second gene, second tissue
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.00012453225502289452
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                # "chr1_33085456_C_G_b38",  # remove
            },
            0.002838611117020821,
        ),
        # same case, but remove one SNP per gene/tissue pair
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: -0.010108294974588818
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                # "chr1_27636786_T_C_b38",  # remove
                #  Artery_Tibial
                # "chr1_27631734_A_G_b38",  # remove
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                # "chr1_33059142_T_A_b38",  # remove
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                # "chr1_33085456_C_G_b38",  # remove
            },
            0.003082718792811474,
        ),
        # same case, but remove all SNPs for the first gene, should be None
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: None
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                # "chr1_27634281_G_A_b38",  # remove
                # "chr1_27636786_T_C_b38",  # remove
                #  Artery_Tibial
                # "chr1_27631734_A_G_b38",  # remove
                # "chr1_27634321_C_G_b38",  # remove
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            None,
        ),
        # case with high correlation, all SNPs selected
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.8124182460001728
        (
            "ENSG00000180596",
            ("Small_Intestine_Terminal_Ileum", "Uterus"),
            "ENSG00000180573",
            (
                "Brain_Cerebellum",
                "Esophagus_Gastroesophageal_Junction",
                "Artery_Coronary",
            ),
            {
                # first gene:
                #  Small_Intestine_Terminal_Ileum
                "chr6_26124075_T_C_b38",
                "chr6_26124202_C_T_b38",
                #  Uterus
                "chr6_26124075_T_C_b38",
                "chr6_26124406_C_T_b38",
                # second gene:
                #  Brain_Cerebellum
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
                "chr6_26124406_C_T_b38",
                #  Esophagus_Gastroesophageal_Junction
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
                # Artery_Coronary
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
            },
            0.8234178806813264,
        ),
        # same case, with at least one SNP remove from each gene/tissue pair
        #  The selected SNPs removes the first tissue of the first gene
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.698593658666404
        (
            "ENSG00000180596",
            ("Small_Intestine_Terminal_Ileum", "Uterus"),
            "ENSG00000180573",
            (
                "Brain_Cerebellum",
                "Esophagus_Gastroesophageal_Junction",
                "Artery_Coronary",
            ),
            {
                # first gene:
                #  Small_Intestine_Terminal_Ileum
                # "chr6_26124075_T_C_b38",  # remove, this removes this tissue
                "chr6_26124202_C_T_b38",  # this SNP is not in the genotype
                #  Uterus
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124406_C_T_b38",
                # second gene:
                #  Brain_Cerebellum
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
                "chr6_26124406_C_T_b38",
                #  Esophagus_Gastroesophageal_Junction
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
                # Artery_Coronary
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
            },
            0.7098608458879089,
        ),
        # same case, with other SNPs removed, only one shared variant is left,
        #  and the correlation is perfect (1.0)
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 1.0
        (
            "ENSG00000180596",
            ("Small_Intestine_Terminal_Ileum", "Uterus"),
            "ENSG00000180573",
            (
                "Brain_Cerebellum",
                "Esophagus_Gastroesophageal_Junction",
                "Artery_Coronary",
            ),
            {
                # first gene:
                #  Small_Intestine_Terminal_Ileum
                "chr6_26124075_T_C_b38",
                # "chr6_26124202_C_T_b38",    # this SNP is not in the genotype
                #  Uterus
                "chr6_26124075_T_C_b38",
                # "chr6_26124406_C_T_b38",  # removed
                # second gene:
                #  Brain_Cerebellum
                "chr6_26124075_T_C_b38",
                # "chr6_26124015_G_A_b38",  # removed
                # "chr6_26124406_C_T_b38",  # (same as other one)
                #  Esophagus_Gastroesophageal_Junction
                "chr6_26124075_T_C_b38",
                # "chr6_26124015_G_A_b38",  # (same as other one)
                # Artery_Coronary
                "chr6_26124075_T_C_b38",
                # "chr6_26124015_G_A_b38",  # (same as other one)
            },
            1.0,
        ),
    ],
)
def test_ssm_correlation_1000G_using_subsets_tissues_and_subsets_of_snps(
    gene1_id, gene1_tissues, gene2_id, gene2_tissues, snps_subset, expected_corr
):
    def compute_ssm_correlation(g1, g1_tis, g2, g2_tis):
        return g1.get_ssm_correlation(
            other_gene=g2,
            tissues=g1_tis,
            other_tissues=g2_tis,
            snps_subset=frozenset(snps_subset) if snps_subset is not None else None,
            reference_panel="1000G",
            model_type="MASHR",
            use_within_distance=False,
        )

    gene1 = Gene(ensembl_id=gene1_id)
    gene2 = Gene(ensembl_id=gene2_id)

    genes_corr = compute_ssm_correlation(gene1, gene1_tissues, gene2, gene2_tissues)
    if expected_corr is not None:
        assert genes_corr is not None
        assert isinstance(genes_corr, float)
        assert genes_corr == pytest.approx(expected_corr, rel=5e-3)

        # check symmetry
        assert compute_ssm_correlation(
            gene2, gene2_tissues, gene1, gene1_tissues
        ) == pytest.approx(genes_corr, rel=1e-10)
    else:
        assert genes_corr is None

        # check symmetry
        assert (
            compute_ssm_correlation(gene2, gene2_tissues, gene1, gene1_tissues) is None
        )


@pytest.mark.parametrize(
    "gene1_id,gene1_tissues,gene2_id,gene2_tissues,snps_subset,expected_corr",
    [
        # All these cases were generated using the file:
        #  tests/test_cases/multixcan.py
        #
        # case where all SNPs are used (at least 2 SNPs per gene per tissue)
        #  I use this case for comparison with other cases below
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.010994204539102827
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            None,
            0.003654579397327897,
        ),
        # exactly the same case, here I just specify all the SNPs manually (so
        #  it has to return the same correlation)
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: same as before
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            0.003654579397327897,
        ),
        # same case, but some SNPs are removed in the first gene, first tissue
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.009420039235209504
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                # "chr1_27634281_G_A_b38",  # remove the one with largest effect
                "chr1_27636786_T_C_b38",
                #  Artery_Tibial
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            0.003515089066714288,
        ),
        # same case, but remove one SNP per gene/tissue pair
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: 0.005248421642129091
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                "chr1_27634281_G_A_b38",
                # "chr1_27636786_T_C_b38",  # remove
                #  Artery_Tibial
                # "chr1_27631734_A_G_b38",  # remove
                "chr1_27634321_C_G_b38",
                # second gene:
                #  Nerve_Tibial
                # "chr1_33059142_T_A_b38",  # remove
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                # "chr1_33085456_C_G_b38",  # remove
            },
            0.002813674962088606,
        ),
        # same case, but remove all SNPs for the first gene, should be None
        #  FGR (1p35.3) and AK2 (1p35.1) - corr ssm: None
        (
            "ENSG00000000938",
            ("Thyroid", "Artery_Tibial"),
            "ENSG00000004455",
            ("Nerve_Tibial", "Liver"),
            {
                # first gene:
                #  Thyroid
                # "chr1_27634281_G_A_b38",  # remove
                # "chr1_27636786_T_C_b38",  # remove
                #  Artery_Tibial
                # "chr1_27631734_A_G_b38",  # remove
                # "chr1_27634321_C_G_b38",  # remove
                # second gene:
                #  Nerve_Tibial
                "chr1_33059142_T_A_b38",
                "chr1_33080995_A_G_b38",
                #  Liver
                "chr1_33080995_A_G_b38",
                "chr1_33085456_C_G_b38",
            },
            None,
        ),
        # case with high correlation, all SNPs selected
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.5838022121737921
        (
            "ENSG00000180596",
            ("Small_Intestine_Terminal_Ileum", "Uterus"),
            "ENSG00000180573",
            (
                "Brain_Cerebellum",
                "Esophagus_Gastroesophageal_Junction",
                "Artery_Coronary",
            ),
            {
                # first gene:
                #  Small_Intestine_Terminal_Ileum
                "chr6_26124075_T_C_b38",
                "chr6_26124202_C_T_b38",
                #  Uterus
                "chr6_26124075_T_C_b38",
                "chr6_26124406_C_T_b38",
                # second gene:
                #  Brain_Cerebellum
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
                "chr6_26124406_C_T_b38",
                #  Esophagus_Gastroesophageal_Junction
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
                # Artery_Coronary
                "chr6_26124075_T_C_b38",
                "chr6_26124015_G_A_b38",
            },
            0.5790480834609772,
        ),
        # same case, with at least one SNP remove from each gene/tissue pair
        #  The selected SNPs removes the first tissue of the first gene
        #  HIST1H2BC (6p22.2) and HIST1H2AC (6p22.2) - corr ssm: 0.6677359957181787
        (
            "ENSG00000180596",
            ("Small_Intestine_Terminal_Ileum", "Uterus"),
            "ENSG00000180573",
            (
                "Brain_Cerebellum",
                "Esophagus_Gastroesophageal_Junction",
                "Artery_Coronary",
            ),
            {
                # first gene:
                #  Small_Intestine_Terminal_Ileum
                # "chr6_26124075_T_C_b38",  # remove, this removes this tissue
                "chr6_26124202_C_T_b38",  # this SNP is not in the genotype
                #  Uterus
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124406_C_T_b38",
                # second gene:
                #  Brain_Cerebellum
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
                "chr6_26124406_C_T_b38",
                #  Esophagus_Gastroesophageal_Junction
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
                # Artery_Coronary
                # "chr6_26124075_T_C_b38",  # (same as other one)
                "chr6_26124015_G_A_b38",
            },
            0.6760669821626591,
        ),
    ],
)
def test_ssm_correlation_GTEX_V8_using_subsets_tissues_and_subsets_of_snps(
    gene1_id, gene1_tissues, gene2_id, gene2_tissues, snps_subset, expected_corr
):
    def compute_ssm_correlation(g1, g1_tis, g2, g2_tis):
        return g1.get_ssm_correlation(
            other_gene=g2,
            tissues=g1_tis,
            other_tissues=g2_tis,
            snps_subset=frozenset(snps_subset) if snps_subset is not None else None,
            reference_panel="GTEX_V8",
            model_type="MASHR",
            use_within_distance=False,
        )

    gene1 = Gene(ensembl_id=gene1_id)
    gene2 = Gene(ensembl_id=gene2_id)

    genes_corr = compute_ssm_correlation(gene1, gene1_tissues, gene2, gene2_tissues)
    if expected_corr is not None:
        assert genes_corr is not None
        assert isinstance(genes_corr, float)
        assert genes_corr == pytest.approx(expected_corr, rel=5e-3)

        # check symmetry
        assert compute_ssm_correlation(
            gene2, gene2_tissues, gene1, gene1_tissues
        ) == pytest.approx(genes_corr, rel=1e-10)
    else:
        assert genes_corr is None

        # check symmetry
        assert (
            compute_ssm_correlation(gene2, gene2_tissues, gene1, gene1_tissues) is None
        )


def test_ssm_correlation_same_gene():
    # ENSG00000122025
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")

    genes_corr = gene1.get_ssm_correlation(gene1)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(1.0)


def test_ssm_correlation_same_gene_using_within_distance():
    # ENSG00000122025
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")

    genes_corr = gene1.get_ssm_correlation(gene1, use_within_distance=True)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(1.0)

    genes_corr = gene1.get_ssm_correlation(gene1, use_within_distance=False)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == pytest.approx(1.0)


def test_ssm_correlation_genes_in_different_chromosomes():
    # ENSG00000122025
    # FLT3
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000122025")

    # ENSG00000175130
    # MARCKSL1
    # chr 1
    gene2 = Gene(ensembl_id="ENSG00000175130")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 0.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == 0.0


def test_ssm_correlation_genes_in_close_bands_not_within_distance():
    # UPF3A
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000169062")

    # EFNB2
    # chr 13
    gene2 = Gene(ensembl_id="ENSG00000125266")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 0.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == pytest.approx(genes_corr, rel=1e-10)


def test_ssm_correlation_genes_in_same_band_not_within_distance():
    # TNFSF13B
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000102524")

    # TPP2
    # chr 13
    gene2 = Gene(ensembl_id="ENSG00000134900")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 0.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == pytest.approx(genes_corr, rel=1e-10)


def test_ssm_correlation_first_gene_without_prediction_models():
    # WNT10A - 2q35
    # this gene does not have prediction models
    gene1 = Gene(ensembl_id="ENSG00000135925")

    # ATIC - 2q35
    gene2 = Gene(ensembl_id="ENSG00000138363")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is None


def test_ssm_correlation_second_gene_without_prediction_models():
    # ATIC - 2q35
    gene1 = Gene(ensembl_id="ENSG00000138363")

    # WNT10A - 2q35
    # this gene does not have prediction models
    gene2 = Gene(ensembl_id="ENSG00000135925")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is None


@pytest.mark.skip(
    reason="not necessary, since the final matrix is still not positive definite, so fixing this issues does not seem important"
)
def test_ssm_correlation_correlation_maximum_value_is_always_one():
    # without checking maximum values, the pair of genes below return a
    # correlation of 1.0000000000000002

    # MPV17 - 2p23.3
    gene1 = Gene(ensembl_id="ENSG00000115204")

    # GTF3C2 - 2p23.3
    gene2 = Gene(ensembl_id="ENSG00000115207")

    genes_corr = gene1.get_ssm_correlation(gene2, reference_panel="1000G")
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 1.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1, reference_panel="1000G") == 1.0


def test_ssm_correlation_correlation_with_condition_number():
    # HIST3H2A (1q42.13)
    gene1 = Gene(ensembl_id="ENSG00000181218")

    # HIST3H2BB (1q42.13)
    gene2 = Gene(ensembl_id="ENSG00000196890")

    genes_corr = gene1.get_ssm_correlation(
        gene2, reference_panel="1000G", condition_number=30
    )
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert 0 <= genes_corr <= 1.0

    # now check that with a different condition number, results should be
    # different
    new_genes_corr = gene1.get_ssm_correlation(
        gene2, reference_panel="1000G", condition_number=10
    )
    assert not (new_genes_corr == pytest.approx(genes_corr))


def test_gene_within_distance():
    # ENSG00000073910
    # FRY
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000073910")

    # ENSG00000133101
    # CCNA1
    # chr 13
    gene2 = Gene(ensembl_id="ENSG00000133101")

    assert not gene1.within_distance(gene2, 1e6)
    assert gene1.within_distance(gene2, 5e6)

    # ENSG00000073910
    # SDCCAG8
    # chr 1
    gene1 = Gene(ensembl_id="ENSG00000054282")

    # ENSG00000133101
    # AKT3
    # chr 1
    gene2 = Gene(ensembl_id="ENSG00000117020")

    assert gene1.within_distance(gene2, 1)
    assert gene1.within_distance(gene2, 1e6)
    assert gene1.within_distance(gene2, 5e6)
    assert gene1.within_distance(gene2, 10e6)

    # SDCCAG8
    # chr 1
    gene1 = Gene(ensembl_id="ENSG00000054282")

    # ADSS
    # chr 1
    gene2 = Gene(ensembl_id="ENSG00000035687")

    assert not gene1.within_distance(gene2, 1e3)
    assert not gene1.within_distance(gene2, 1e4)
    assert not gene1.within_distance(gene2, 1e5)
    assert gene1.within_distance(gene2, 1e6)
    assert gene1.within_distance(gene2, 5e6)
    assert gene1.within_distance(gene2, 10e6)


def test_ssm_correlation_genes_far_apart_not_within_distance():
    # ENSG00000188976
    # NOC2L
    # chr 1p36.33
    gene1 = Gene(ensembl_id="ENSG00000188976")

    # ENSG00000238243
    # OR2W3
    # chr 1q44
    gene2 = Gene(ensembl_id="ENSG00000238243")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr == 0.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == 0.0


def test_ssm_correlation_genes_in_same_band_within_distance():
    # COL4A2
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000134871")

    # COL4A1
    # chr 13
    gene2 = Gene(ensembl_id="ENSG00000187498")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr > 0.00

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == pytest.approx(genes_corr, rel=1e-10)


def test_ssm_correlation_genes_in_same_band_within_distance_2():
    # IRS2
    # chr 13
    gene1 = Gene(ensembl_id="ENSG00000185950")

    # COL4A1
    # chr 13
    gene2 = Gene(ensembl_id="ENSG00000187498")

    genes_corr = gene1.get_ssm_correlation(gene2)
    assert genes_corr is not None
    assert isinstance(genes_corr, float)
    assert genes_corr >= 0.0

    # check symmetry
    assert gene2.get_ssm_correlation(gene1) == pytest.approx(genes_corr, rel=1e-10)


@pytest.mark.parametrize(
    "tissue,snps_list,variances",
    [
        (
            "Lung",
            ("chr1_27634321_C_G_b38",),
            [
                0.1360539913529474,
            ],
        ),
        (
            "Whole_Blood",
            ("chr7_26912520_T_C_b38",),
            [
                0.5072360250445618,
            ],
        ),
        (
            "Artery_Tibial",
            (
                "chr1_27631734_A_G_b38",
                "chr1_27634321_C_G_b38",
            ),
            [
                0.13112781954887204,
                0.1326271561256085,
            ],
        ),
    ],
)
def test_get_snps_variance(tissue, snps_list, variances):
    obs_vars = Gene.get_snps_variance(tissue, snps_list, model_type="MASHR")
    exp_vars = pd.Series({s: v for s, v in zip(snps_list, variances)})
    pd.testing.assert_series_equal(obs_vars, exp_vars)
