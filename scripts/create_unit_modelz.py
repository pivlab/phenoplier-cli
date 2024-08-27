import pandas as pd

if __name__ == "__main__":
    multiplier_z_path = "/tmp/phenoplier/data/multiplier/multiplier_model_z.pkl"

    multiplier_z = pd.read_pickle(multiplier_z_path)
    # Save LV1, LV987, and LV 500
    unittest_multiplier_z = multiplier_z[['LV1', 'LV987', 'LV500']]
    print(unittest_multiplier_z)
    # Save the model
    unittest_multiplier_z.to_pickle("./unittest_multiplier_z.pkl")
