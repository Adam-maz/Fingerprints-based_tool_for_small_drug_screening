import os
import joblib
import numpy as np
import pandas as pd

from rdkit import Chem
from rdkit.Chem.AllChem import GetMorganGenerator


class Predictor:
    def __init__(self):
        self.model = None
        self.predict_df = None
        self.X = None

    def model_importer(self):
        for elem in os.listdir(os.getcwd()):
            if elem.endswith(".joblib"):
                self.model = joblib.load(elem)
                print(f"Model loaded from: {elem}")
                return self.model
        raise FileNotFoundError("No .joblib file found in the directory.")

    def predict_data_importer(self):
        for elem in os.listdir(os.getcwd()):
            if elem.endswith(".csv"):
                self.predict_df = pd.read_csv(elem)
                print(f"Prediction data loaded from: {elem}")
                return self.predict_df
        raise FileNotFoundError("No .csv file found in the directory.")

    def fps_generator(self):
        if self.predict_df is None:
            raise ValueError("Prediction data not loaded. Call `predict_data_importer` first.")

        morgan_gen = GetMorganGenerator(radius=1, fpSize=4096)
        fingerprints = []

        for sm in self.predict_df["smiles"]:
            mol = Chem.MolFromSmiles(sm)
            if mol is None:
                raise ValueError(f"Invalid SMILES string: {sm}")
            fingerprints.append(morgan_gen.GetFingerprint(mol).ToBitString())

        self.X = np.array([list(map(int, fp)) for fp in fingerprints])
        print("Fingerprints generated.")
        print()
        return self.X


def main():
    obj = Predictor()
    try:
        obj.model_importer()
        obj.predict_data_importer()
        X = obj.fps_generator()

        # Ensure the model is loaded
        if obj.model is None:
            raise ValueError("Model is not loaded. Please check the directory.")

        # Predict using the model
        scores = obj.model.predict(X)
        print('============================================')
        print('Output: ')
        for value, mol_id in zip(scores, obj.predict_df["id"]):
            print(f"Id: {mol_id} ==> Activity: {value}")
        print('============================================')
        print()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
