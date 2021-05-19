import core
import cv2
import logging
import time

def main():
    #클라이언트에게 통보하기 위해서 소켓 생성
    sender = core.SocketUDPUtil(9600)

    #사람을 탐지할 때 사용할 디텍터 생성
    #cfg경로, weights경로, 네트워크 사이즈를 입력(32의 배수)
    #지금 사용하는 cfg, weights는 coco dataset으로 학습된 모델임
    detector = core.DarknetUtil("yolov4-tiny.cfg", "yolov4-tiny.weights", (608, 608))

    #통보받을 클라이언트의 주소:포트 리스트를 가져옴
    with open("receiver-list.txt", "rt") as f:
        receiverList = [receiver.replace("\n", "").split(":") for receiver in f.readlines()]

    [print(f"target __ {addr} : {port}") for addr, port in receiverList]
    
    #USB로 연결된 비디오 카메라를 오픈함
    cap = cv2.VideoCapture(0)

    #최소 탐지율
    min_thresh = 0.8

    #카메라가 열렸다면
    while cap.isOpened():
        try:
            #비디오 프레임을 가져옴
            success, frame = cap.read()
            if not success:
                logging.warning(f"프레임을 가져오는데 실패함...")
                continue

            #가져온 프레임에서 탐지 시도
            result = detector.detect(frame, min_thresh)
            find = False

            #탐지한게 있다면
            if result:
                for data in result:
                    #아이디 0 = 사람
                    #탐지 결과에 사람이 있고 탐지율이 최소 탐지율 이상이라면
                    #탐지 플래그를 올림
                    if data["id"] == 0 and data["thresh"] > min_thresh:
                        find = True
                        break


            if find:
                #클라이언트들에게 찾았다고 통보함
                [sender.send((addr, int(port)), "detect\0".encode("utf-16le")) for addr, port in receiverList]
                #for info in result:
                    #cv2.rectangle(frame, (info["x"], info["y"]), (info["x"] + info["w"], info["y"] + info["h"]), (0, 0, 255), 2)
                    #cv2.imshow("view", frame)
            
            else:
                #찾지 못했다고 통보함
                [sender.send((addr, int(port)), "not detect\0".encode("utf-16le")) for addr, port in receiverList]

            #100ms대기
            time.sleep(0.1)
            #if cv2.waitKey(100) & 0xff == 27:
            #    cv2.destroyAllWindows()


        except KeyboardInterrupt as e:
            logging.info("exit!")
            break

    cap.release()


        

if __name__ == "__main__":
    main()