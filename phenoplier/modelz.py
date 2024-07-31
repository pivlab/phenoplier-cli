import pandas as pd
from phenoplier.config import settings as conf


if __name__ == "__main__":
    multiplier_z = pd.read_pickle(conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])
    multiplier_z = pd.DataFrame.from_dict(multiplier_z['data'])
    print(f"Loading MultiPLIER Z genes from: {conf.GENE_MODULE_MODEL['MODEL_Z_MATRIX_FILE']}")

    multiplier_z.to_pickle("./marc_model_z.pkl")
