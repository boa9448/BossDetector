import core
import cv2
import logging

def main():
    sender = core.SocketUDPUtil(9600)
    detector = core.DarknetUtil("yolov4-tiny.cfg", "yolov4-tiny.weights", (608, 608))
    with open("receiver-list.txt", "rt") as f:
        receiverList = [receiver.replace("\n", "").split(":") for receiver in f.readlines()]

    [print(f"target __ {addr} : {port}") for addr, port in receiverList]
    
    cap = cv2.VideoCapture(0)

    min_thresh = 0.8
    while cap.isOpened():
        try:
            success, frame = cap.read()
            if not success:
                logging.warning(f"프레임을 가져오는데 실패함...")
                continue

            result = detector.detect(frame, min_thresh)
            find = False
            if result:
                for data in result:
                    if data["id"] == 0 and data["thresh"] > min_thresh:
                        find = True
                        break


            if find:
                for info in result:
                    cv2.rectangle(frame, (info["x"], info["y"]), (info["x"] + info["w"], info["y"] + info["h"]), (0, 0, 255), 2)
                    [sender.send((addr, int(port)), "detect\0".encode("utf-16le")) for addr, port in receiverList]
                    cv2.imshow("view", frame)
            
            else:
                [sender.send((addr, int(port)), "not detect\0".encode("utf-16le")) for addr, port in receiverList]

            if cv2.waitKey(100) & 0xff == 27:
                cv2.destroyAllWindows()


        except KeyboardInterrupt as e:
            logging.info("exit!")
            break

    cap.release()


        

if __name__ == "__main__":
    main()