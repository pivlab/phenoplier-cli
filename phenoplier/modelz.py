import pandas as pd
from phenoplier.config import settings as conf


if __name__ == "__main__":
    # multiplier_z = pd.read_pickle(conf.GENE_MODULE_MODEL["MODEL_Z_MATRIX_FILE"])
    multiplier_z = pd.read_pickle("/tmp/phenoplier/data/multiplier/htp_plier_model_k0.75_frac1_Zmatrix.pkl")
    multiplier_z = pd.DataFrame.from_dict(multiplier_z['data'])
    multiplier_z.columns = ['L' + col for col in multiplier_z.columns]
    print(multiplier_z)

    multiplier_z.to_pickle("./marc_model_z.pkl")
