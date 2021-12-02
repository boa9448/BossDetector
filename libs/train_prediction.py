import os
import pickle
from typing import Any


import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC


from . import detection


class SvmUtil:
    def __init__(self):
        self._logger = print

    def __del__(self):
        pass

    @property
    def logger(self) -> Any:
        return self._logger

    @logger.setter
    def logger(self, new_logger : Any) -> None:
        self._logger = new_logger        
    
    def train_svm(self, data : list, label : list) -> SVC:
        self.le = LabelEncoder()
        labels = self.le.fit_transform(label)
        
        self.logger("[INFO] training model...")
        self.model = SVC(C=1.0, kernel="linear", probability=True)
        self.model.fit(data, labels)
        self.logger("[INFO] train end")

        return self.model

    def save_svm(self, save_path : str) -> None:
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        with open(os.path.join(save_path, "svm_model"), "wb") as f:
            f.write(pickle.dumps(self.model))
            f.close()

        with open(os.path.join(save_path, "le"), "wb") as f:
            f.write(pickle.dumps(self.le))
            f.close()

    def load_svm(self, load_path : str) -> None:
        self.model = pickle.loads(open(os.path.join(load_path, "svm_model"), "rb").read())
        self.le = pickle.loads(open(os.path.join(load_path, "le"), "rb").read())

    def predict(self, data) -> tuple:
        results = self.model.predict_proba(data)
        indexes = [np.argmax(result) for result in results]

        probabilities = [float(result[idx]) for result, idx in zip(results, indexes)]
        names = [str(self.le.classes_[idx]) for idx in indexes]

        return tuple(zip(names, probabilities))

    def get_labels(self) -> tuple:
        return self.le.classes_