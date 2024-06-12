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
from phenoplier.commands.enums import Cohort, RefPanel, EqtlModel
from phenoplier.commands.utils import load_settings_files


def generate(
    cohort_name:        Annotated[Cohort, typer.Option("--cohort-name", "-c", help="Cohort name")],
    reference_panel:    Annotated[RefPanel, typer.Option("--reference-panel", "-r", help="Reference panel such as 1000G or GTEX_V8")],
    eqtl_model:         Annotated[EqtlModel, typer.Option("--eqtl-model", "-m", help="Prediction models such as MASHR or ELASTIC_NET")],
    lv_code:            Annotated[int, typer.Option("--lv-code", "-l", min=1, help="The code of the latent variable (LV) to compute the correlation matrix for")],
    lv_percentile:      Annotated[float, typer.Option("--lv-percentile", "-e", min=0.0, max=1.0, help="A number from 0.0 to 1.0 indicating the top percentile of the genes in the LV to keep")] = 0.05,
    project_dir:        Annotated[Path, typer.Option("--project-dir", "-p", help="Project directory")] = conf.CURRENT_DIR,
):
    """
    Computes an LV-specific correlation matrix by using the top genes in that LV only.
    """
    def validate_inputs(cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile):
        assert cohort_name is not None and len(cohort_name) > 0, "A cohort name must be given"
        assert reference_panel is not None and len(reference_panel) > 0, "A reference panel must be given"
        assert eqtl_model is not None and len(eqtl_model) > 0, "A prediction/eQTL model must be given"
        assert lv_code is not None and len(lv_code) > 0, "An LV code must be given"
        if lv_percentile is not None:
            lv_percentile = float(lv_percentile)
        return cohort_name.lower(), reference_panel.lower(), eqtl_model.lower(), lv_code, lv_percentile

    cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile = validate_inputs(cohort_name, reference_panel, eqtl_model, lv_code, lv_percentile)

    load_settings_files(project_dir)

    OUTPUT_DIR_BASE = conf.RESULTS["GLS"] / "gene_corrs" / "cohorts" / cohort_name / reference_panel / eqtl_model
    gene_corrs_dict = {f.name: pd.read_pickle(f) for f in OUTPUT_DIR_BASE.glob("gene_corrs-symbols*.pkl")}
    multiplier_z = pd.read_pickle(conf.MULTIPLIER["MODEL_Z_MATRIX_FILE"])

    def exists_df(output_dir, base_filename):
        full_filepath = output_dir / (base_filename + ".npz")
        return full_filepath.exists()

    def store_df(output_dir, nparray, base_filename):
        if base_filename in ("metadata", "gene_names"):
            np.savez_compressed(output_dir / (base_filename + ".npz"), data=nparray)
        else:
            sparse.save_npz(output_dir / (base_filename + ".npz"), sparse.csc_matrix(nparray), compressed=False)

    def get_output_dir(gene_corr_filename):
        path = OUTPUT_DIR_BASE / gene_corr_filename
        assert path.exists()
        return path.with_suffix(".per_lv")

    def compute_chol_inv(lv_code):
        for gene_corr_filename, gene_corrs in gene_corrs_dict.items():
            output_dir = get_output_dir(gene_corr_filename)
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

    lvs_chunks = [[lv_code]]

    with ProcessPoolExecutor(max_workers=1) as executor, tqdm(total=len(lvs_chunks), ncols=100) as pbar:
        tasks = [executor.submit(compute_chol_inv, chunk) for chunk in lvs_chunks]
        for future in as_completed(tasks):
            res = future.result()
            pbar.update(1)
