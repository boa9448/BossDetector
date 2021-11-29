import cv2

import env
from libs.detection import FaceDetector


cap = cv2.VideoCapture(0)
detector = FaceDetector()
while cap.isOpened():
    success, img = cap.read()
    if not success:
        continue

    results = detector.detect(img)
    img = detector.draw(img, results)
    cv2.imshow("view", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()