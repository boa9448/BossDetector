import cv2
import numpy as np


def cv2_imread(filename : str, flags : int = cv2.IMREAD_COLOR) -> np.ndarray:
    raw = np.fromfile(filename, np.uint8)
    img = cv2.imdecode(raw, flags)

    return img