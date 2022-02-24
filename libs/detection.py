import cv2
import numpy as np
import mediapipe as mp


from . import exception


mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


FaceDetectOutput = list[tuple[int, int, int, int]]

class FaceDetector:

    def __init__(self, min_detection_confidence : float = 0.5):
        self.mp_face = mp_face_detection.FaceDetection(model_selection = 0
                                                    , min_detection_confidence = min_detection_confidence)

    def __del__(self):
        self.mp_face.close()

    def detect(self, img : np.ndarray) -> FaceDetectOutput:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.mp_face.process(img)

        if not results.detections:
            return list()

        face_list = list()
        h, w, c = img.shape
        for detection in results.detections:
            relative_bounding_box = detection.location_data.relative_bounding_box
            x = int(relative_bounding_box.xmin * w)
            y = int(relative_bounding_box.ymin * h)
            width = int(relative_bounding_box.width * w)
            height = int(relative_bounding_box.height * h)

            face_list.append((x, y, width, height))

        return face_list

    def draw(self, img : np.ndarray, boxes : FaceDetectOutput) -> np.ndarray:
        for x, y, w, h in boxes:
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return img

    def crop(self, img : np.ndarray, boxes : FaceDetectOutput) -> list[np.ndarray]:
        img_list = list()
        for x, y, w, h in boxes:
            roi = img[y : y + h, x : x + w]
            img_list.append(roi)

        return img_list

    def detect_crop(self, img : np.ndarray) -> list[np.ndarray]:
        face_list = self.detect(img)
        return self.crop(img, face_list)



if __name__ == "__main__":
    pass