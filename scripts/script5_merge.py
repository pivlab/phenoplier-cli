import pandas as pd

if __name__ == "__main__":
    meta_data = "/tmp/phenoplier/results/gls/PhenomeXcan S-MultiXcan.tsv"
    df = pd.read_csv(meta_data, sep="\t")

    fields_to_keed = ["full_code", "short_code", "description", "type", "n", "n_cases", "n_controls", "source"]
    print(df)
