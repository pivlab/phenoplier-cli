import subprocess
import re
from pathlib import Path

if __name__ == "__main__":
    # Define the directories and file paths
    INPUT_SMULTIXCAN_DIR = "/tmp/phenoplier/data/smultixcan/alpine/rapid_gwas_project"
    OUTPUT_DIR = "/tmp/phenoplier/results/gls/lv1-lv76-all-traits"
    GENE_CORR_FILE = "/tmp/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv"

    results_files = list(Path(INPUT_SMULTIXCAN_DIR).rglob("*.tsv.gz"))
    pheno_pattern = re.compile(r"smultixcan_(?P<pheno_code>.+)_ccn30.tsv.gz")
    pheno_codes = [pheno_pattern.search(f.name).group("pheno_code") for f in results_files]
    assert len(results_files) == len(pheno_codes)

    # List of pheno_ids
    # selectd_pheno_ids = ["21001_raw", "23104_raw", "E4_OBESITY", "NAFLD", "20002_1223", "E66", "E4_OBESITYNAS", "21002_raw", "3160_raw"]

    # Function to run the phenoplier command
    def run_phenoplier(pheno_id):
        print(f"Running phenoplier for pheno_id: {pheno_id}")
        command = [
            "poetry", "run", "python", "-m", "phenoplier", "run", "regression",
            "-i", f"{INPUT_SMULTIXCAN_DIR}/smultixcan_{pheno_id}_ccn30.tsv.gz",
            "-o", f"{OUTPUT_DIR}/gls_phenoplier-{pheno_id}.tsv.gz",
            "-g", GENE_CORR_FILE,
            "-c", "default",
            "-m", "sub",
            "-d", "keep-first",
            "-f", "/tmp/phenoplier/data/multiplier/marc_model_z.pkl",
            "-l", "LV1 LV3 LV28 LV34 LV37 LV43 LV76"
            # "-l", "LV3 LV24 LV36 LV37 LV76"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error running phenoplier for pheno_id: {pheno_id}")
            print(result.stderr)

    # Loop through each pheno_id and run the command
    for pheno_id in pheno_codes:
        run_phenoplier(pheno_id)
