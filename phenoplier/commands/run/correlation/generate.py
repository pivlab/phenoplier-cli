from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Annotated
from pathlib import Path

import typer
import pandas as pd
import numpy as np
from scipy import sparse
from tqdm import tqdm

from phenoplier.config import settings as conf
from phenoplier.gls import GLSPhenoplier
from phenoplier.commands.util.enums import Cohort, RefPanel, EqtlModel
from phenoplier.constants.cli import Corr_Generate_Args as Args
from phenoplier.commands.util.utils import load_settings_files


def exists_df(output_dir, base_filename):
    full_filepath = output_dir / (base_filename + ".npz")
    return full_filepath.exists()


def store_df(output_dir, nparray, base_filename):
    if base_filename in ("metadata", "gene_names"):
        np.savez_compressed(output_dir / (base_filename + ".npz"), data=nparray)
    else:
        sparse.save_npz(output_dir / (base_filename + ".npz"), sparse.csc_matrix(nparray), compressed=False)


def get_output_dir(gene_corr_filename, OUTPUT_DIR_BASE):
    path = OUTPUT_DIR_BASE / gene_corr_filename
    assert path.exists()
    return path.with_suffix(".per_lv")


def compute_chol_inv(lv_code, gene_corrs_dict, multiplier_z, OUTPUT_DIR_BASE, reference_panel, eqtl_model, lv_percentile):
    for gene_corr_filename, gene_corrs in gene_corrs_dict.items():
        output_dir = get_output_dir(gene_corr_filename, OUTPUT_DIR_BASE)
        output_dir.mkdir(parents=True, exist_ok=True)

        lv_data = multiplier_z[lv_code]
        corr_mat_sub = GLSPhenoplier.get_sub_mat(gene_corrs, lv_data, lv_percentile)
        store_df(output_dir, corr_mat_sub.to_numpy(), f"{lv_code}_corr_mat")

        chol_mat = np.linalg.cholesky(corr_mat_sub)
        chol_inv = np.linalg.inv(chol_mat)
        store_df(output_dir, chol_inv, lv_code)

        if not exists_df(output_dir, "metadata"):
            metadata = np.array([reference_panel, eqtl_model])
            store_df(output_dir, metadata, "metadata")

        if not exists_df(output_dir, "gene_names"):
            gene_names = np.array(gene_corrs.index.tolist())
            store_df(output_dir, gene_names, "gene_names")



def generate(
    cohort_name:        Annotated[Cohort, Args.COHORT_NAME.value],
    reference_panel:    Annotated[RefPanel, Args.REFERENCE_PANEL.value],
    eqtl_model:         Annotated[EqtlModel, Args.EQTL_MODEL.value],
    lv_code:            Annotated[int, Args.LV_CODE.value],
    lv_percentile:      Annotated[float, Args.LV_PERCENTILE.value] = 0.05,
    project_dir:        Annotated[Path, Args.PROJECT_DIR.value] = conf.CURRENT_DIR,
):
    """
    Computes an LV-specific correlation matrix by using the top genes in that LV only.
    """

    eqtl_model = eqtl_model.lower()
    reference_panel = reference_panel.lower()
    lv_code = "LV" + str(lv_code)
    load_settings_files(project_dir)

    OUTPUT_DIR_BASE = Path(conf.RESULTS["GLS"]) / "gene_corrs" / "cohorts" / cohort_name / reference_panel / eqtl_model
    gene_corrs_dict = {f.name: pd.read_pickle(f) for f in OUTPUT_DIR_BASE.glob("gene_corrs-symbols*.pkl")}
    multiplier_z = pd.read_pickle(conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])

    lvs_chunks = [[lv_code]]

    with ProcessPoolExecutor(max_workers=1) as executor, tqdm(total=len(lvs_chunks), ncols=100) as pbar:
        tasks = [
            executor.submit(compute_chol_inv, chunk[0], gene_corrs_dict, multiplier_z, OUTPUT_DIR_BASE, reference_panel, eqtl_model, lv_percentile)
            for chunk in lvs_chunks
        ]
        for future in as_completed(tasks):
            res = future.result()
            pbar.update(1)

    print(f"Computation for {lv_code} done. Output to {OUTPUT_DIR_BASE}")

