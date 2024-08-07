import subprocess
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

if __name__ == "__main__":
    # Define the directories and file paths
    INPUT_SMULTIXCAN_DIR = "/tmp/phenoplier/data/smultixcan/alpine/rapid_gwas_project"
    OUTPUT_DIR = "/tmp/phenoplier/results/gls/all-LVs-all-traits"
    LOG_FILE = OUTPUT_DIR + "/phenoplier_output.log"
    GENE_CORR_FILE = "/tmp/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv"

    # Lock for synchronizing log file writes
    log_lock = threading.Lock()

    results_files = list(Path(INPUT_SMULTIXCAN_DIR).rglob("*.tsv.gz"))
    pheno_pattern = re.compile(r"smultixcan_(?P<pheno_code>.+)_ccn30.tsv.gz")
    pheno_codes = [pheno_pattern.search(f.name).group("pheno_code") for f in results_files]
    assert len(results_files) == len(pheno_codes)

    # List of pheno_ids
    # selectd_pheno_ids = ["21001_raw", "23104_raw", "E4_OBESITY", "NAFLD", "20002_1223", "E66", "E4_OBESITYNAS", "21002_raw", "3160_raw"]

    # Function to run the phenoplier command
    def run_phenoplier(pheno_id, lv_code):
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
            "-l", lv_code
            # "-l", "LV3 LV24 LV36 LV37 LV76"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        log_output = f"Output for pheno_id: {pheno_id}, LV: {lv_code}\n{result.stdout}"
        if result.returncode != 0:
            log_output += f"\nError running phenoplier for pheno_id: {pheno_id}, LV: {lv_code}\n{result.stderr}\n"

        # Write to log file with synchronization
        with log_lock:
            with open(LOG_FILE, "a") as log_file:
                log_file.write(log_output + "\n")

    lv_ids = [f"LV{i}" for i in range(1, 118)]
    lv_ids_str = ' '.join(lv_ids)

    # Use ThreadPoolExecutor to run tasks in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for each pheno_id
        futures = [executor.submit(run_phenoplier, pheno_id, lv_ids_str) for pheno_id in pheno_codes]

        # Wait for all futures to complete
        for future in futures:
            future.result()
