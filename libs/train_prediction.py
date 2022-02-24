import os
import pickle
from typing import Any
from glob import glob

import cv2
import numpy as np
import imutils
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC


from . import embed_model_path
from .detection import FaceDetector, FaceDetectOutput
from .utils import cv2_imread


class SvmUtil:
    def __init__(self):
        self._logger = print
        self._detector = FaceDetector()
        self._embedder = cv2.dnn.readNetFromTorch(embed_model_path)

    def __del__(self):
        pass

    @property
    def logger(self) -> Any:
        return self._logger

    @logger.setter
    def logger(self, new_logger : Any) -> None:
        self._logger = new_logger

    def draw(self, img : np.ndarray, boxes : FaceDetectOutput) -> np.ndarray:
        return self._detector.draw(img, boxes)

    def extract(self, img : np.ndarray) -> tuple[FaceDetectOutput, list[Any]]:
        results = self._detector.detect_crop(img)
        if not results:
            return list()

        detection_output, face_list = results
        knownEmbeddings = list()

        for face in face_list:
            h, w, _ = face.shape
            if h == 0 or w == 0:
                continue
            
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                    (96, 96), (0, 0, 0), swapRB=True, crop=False)
            self._embedder.setInput(faceBlob)
            vec = self._embedder.forward()

            # add the name of the person + corresponding face
            # embedding to their respective lists
            knownEmbeddings.append(vec.flatten())

        return detection_output, knownEmbeddings

    def extract_train_dataset(self, dataset_path : str) -> tuple[list, list]:
        file_list = list()
        
        def get_file_list() -> list:
            return glob(os.path.join(dataset_path, "**", "*.*"), recursive = True)

        file_list = get_file_list() if type(dataset_path) == str else dataset_path
        self.logger(f"[INFO] file count : {len(file_list)}")

        name_list = list()
        data_list = list()
        for idx, file in enumerate(file_list):
            self.logger(f"[INFO] process... {idx + 1}/{len(file_list)}")
            name = file.split(os.path.sep)[-2]

            img = cv2_imread(file)
            result = self.extract(img)
            if not result:
                continue
            
            detection_output, embedds = result
            name_list.append(name)
            data_list.append(embedds[0]) #맨 처음 등록된 1개의 정보만 데이터로 등록

        self.logger("done")
        return (name_list, data_list)
    
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