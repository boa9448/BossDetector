import os

import cv2
import numpy as np

import env
from libs import *
from libs.detection import FaceDetectOutput


def draw(img : np.ndarray, detection_output : FaceDetectOutput
                        , predict_output : tuple[tuple[str, float]]) -> np.ndarray:
    
    for detect, predict in zip(detection_output, predict_output):
        label, proba = predict
        x, y, w, h = detect
        is_boss = label == "보스"
        color = (0, 0, 255) if is_boss else (0, 255, 0)
        text = "boss" if is_boss else ""
        img = cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        img = cv2.putText(img, text, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)

    return img


def main():
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    dataset_dir = os.path.abspath(os.path.join(cur_dir, "..", "dataset"))

    classifier = train_prediction.SvmUtil()
    names, datas = classifier.extract_train_dataset(dataset_dir)
    classifier.train_svm(datas, names)
    classifier.save_svm("test_model")

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        results = classifier.extract(img)
        if results:
            detection_output, embeds = results
            results = classifier.predict(embeds)
            img = draw(img, detection_output, results)
        
        cv2.imshow("view", img)
        if cv2.waitKey(1) & 0xff == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

            


if __name__ == "__main__":
    main()