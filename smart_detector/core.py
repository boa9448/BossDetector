import ctypes
import cv2
import numpy as np
import pickle
import socket
from ctypes import wintypes

#UDP소켓 통신용 클래스
class SocketUDPUtil:
    def __init__(self, port = 9500):
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind(("", port))
        
    def __del__(self):
        self.udpSock.close()

    def send(self, addr, data):
        return self.udpSock.sendto(data, addr)

    def recv(self):
        data, addr = self.udpSock.recvfrom(2048)
        return (data, addr)


#opencv dnn + darknet yolov4를 더 쉽게 사용하기 위해서 만든 래퍼 클래스
class DarknetUtil:
    DARKNET_SCALE = 0.00392 #스케일

    def __init__(self, cfgPath, modelPath, netSize):
        """
        cfgPath : cfg파일의 경로
        modelPath : weights파일의 경로
        netSize : 네트워크 입력 사이즈 ex __ (608, 608)
                  32의 배수로 입력
        """

        self.net = cv2.dnn.readNetFromDarknet(cfgPath, modelPath)
        self.width = netSize[0]
        self.height = netSize[1]

    def __del__(self):
        pass


    def detect(self, image, thresh = 0.25):
        #20201227 수정된 부분
        #shape 순서는 height, width, channel 순서임

        #3채널 이상의 이미지가 들어와야함
        Height, Width = image.shape[:2]
        #이미지를 blob형태로 변환함
        #함수의 파라미터는 사용하려는 모델이나 프레임워크에 따라서 달라질 수 있음
        #막 복붙 금지
        blob = cv2.dnn.blobFromImage(image, self.DARKNET_SCALE, (self.width, self.height), (0,0,0), True, crop=False)

        #네트워크에 입력 후 출력을 가져옴
        self.net.setInput(blob)
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        outs = self.net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        #각 출력 계층에 대한 탐지에 대한
        #신뢰도, 클래스 아이디, 바운딩박스 정보를 가져옴
        #confidence, class_id, x, y, w, h
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > thresh:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])


        #비최대 억제
        #김치국 정보는 다음 링크 참조
        #https://dyndy.tistory.com/275
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        #딕셔너리 형태로 변환 후 리턴함
        retBoxes = []
        for i in indices:
            x,y,w,h = boxes[i[0]]
            retBoxes.append({"x":x, "y":y, "w":w, "h":h, "id":class_ids[i[0]], "thresh":confidences[i[0]]})
        
        return retBoxes