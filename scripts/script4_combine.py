import re
from glob import glob
from pathlib import Path
from statsmodels.stats.multitest import multipletests

import pandas as pd

def tsv():
    files = []

    for f in glob("/tmp/phenoplier/results/gls/lv1-lv76-all-traits/*.tsv.gz"):
        files.append(pd.read_csv(f, sep="\t").assign(file=f))


    r = pd.concat(files)

    adj_pval = multipletests(r["pvalue_onesided"], alpha=0.05, method="fdr_bh")

    r = r.assign(fdr=adj_pval[1])

    # save dataframe r to a file
    r.to_csv("/tmp/phenoplier/results/gls/lv1-lv76-all-traits.tsv", sep="\t", index=False)


def pickle(intput_dir: Path, output_dir: Path):
    # INPUT_SMULTIXCAN_DIR = "/tmp/phenoplier/results/gls/lv1-lv76-all-traits"

    results_files = list(intput_dir.rglob("*.tsv.gz"))
    pheno_pattern = re.compile(r"gls_phenoplier-(?P<pheno_code>.+).tsv.gz")
    pheno_codes = [pheno_pattern.search(f.name).group("pheno_code") for f in results_files]

    # Dictionary to hold dataframes for each file
    data_dict = {}

    # Read each file and store in the dictionary with filename as key
    for f in glob(str(input_dir) + "/*.tsv.gz"):
        df = pd.read_csv(f, sep="\t")
        match = pheno_pattern.search(f)
        assert match
        pheno_code = match.group("pheno_code")

        data_dict[pheno_code] = df

    # Save the dictionary of dataframes as a pickle file
    assert len(data_dict.keys()) == 4049, len(data_dict.keys())
    with open(output_dir, "wb") as handle:
        pd.to_pickle(data_dict, handle)


if __name__ == "__main__":
    # input = Path("/tmp/phenoplier/results/gls/lv1-lv76-all-traits.pkl")
    input_dir = Path("/tmp/phenoplier/results/gls/all-LVs-all-traits")
    output_dir = Path("/tmp/phenoplier/results/gls/all-LVs-all-traits.pkl")
    pickle(input_dir, output_dir)

