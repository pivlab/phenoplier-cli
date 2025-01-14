import pickle
import concurrent.futures
import os
import numpy as np
import pandas as pd

from pathlib import Path

N_JOBS = 16
N_SAMPLES = 5
# N_SAMPLES = 50

# Get path from env var PHENOPLIER_RESULTS_GLS_NULL_SIMS_UKB_40PCS
POST_IMPUTED_DIR = Path(os.environ["PHENOPLIER_NULLSIM_RESULTS_DIR"]) / "post_imputed_gwas"

input_files = sorted(list(POST_IMPUTED_DIR.glob("*.txt.gz")))
len(input_files)

# sample files
np.random.seed(0)
input_files = np.random.choice(input_files, size=N_SAMPLES, replace=False)
len(input_files)

# read all GWAS and find a set of common panel_variant_id_values
def _get_gwas_variants(f):
    gwas_data = pd.read_table(f, usecols=["panel_variant_id", "zscore"])
    assert gwas_data["panel_variant_id"].is_unique
    assert gwas_data.shape == gwas_data.dropna().shape
    return f.name, set(gwas_data["panel_variant_id"])

common_variants = set()
last_n_var_ids = -1
with concurrent.futures.ProcessPoolExecutor(max_workers=N_JOBS) as executor:
    for gwas_file_name, gwas_variants in executor.map(_get_gwas_variants, input_files, chunksize=10):
        if len(common_variants) == 0:
            common_variants = gwas_variants
        else:
            common_variants = common_variants.intersection(gwas_variants)
        
        n_var_ids = len(common_variants)
        same_previous = n_var_ids == last_n_var_ids
        last_n_var_ids = n_var_ids
        print(f"{gwas_file_name}, # common variants: {n_var_ids} (same? {same_previous})", flush=True)


with open(POST_IMPUTED_DIR / "common_variant_ids.pkl", 'wb') as f:
    pickle.dump(common_variants, f, protocol=pickle.HIGHEST_PROTOCOL)