import cv2
import numpy as np
import pickle
import socket

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

#추후에 확장을 위한 클래스
class DetectUtil:
    def __init__(self):
        pass

    def __del__(self):
        pass

if __name__ == "__main__":
    #디텍터 생성
    detector = DarknetUtil("yolov4-tiny.cfg", "yolov4-tiny.weights", (608, 608))
    
    #테스트 이미지 불러옴
    img = cv2.imread("test.jpg", cv2.IMREAD_UNCHANGED)

    #이미지에서 디텍션
    min_thresh = 0.7
    resultList = detector.detect(img, min_thresh)

    #찾은 결과에 바운딩 박스만 출력
    for result in resultList:
        cv2.rectangle(img, (result["x"], result["y"]), (result["x"] + result["w"], result["y"] + result["h"]), (0, 255, 0), 2)

    #결과 이미지 표시
    cv2.imshow("view", img)
    cv2.waitKey()
    cv2.destroyAllWindows()
