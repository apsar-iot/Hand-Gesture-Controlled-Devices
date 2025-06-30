import pyfirmata
import cv2
from cvzone.HandTrackingModule import HandDetector

# Arduino setup
comport = 'COM5'                                                                             
board = pyfirmata.Arduino(comport)

# Device labels and pin mapping (skip ring finger)
# Finger indices: 0=Thumb, 1=Index, 2=Middle, 3=Ring, 4=Little
device_map = {
    0: ("Fan", 8),
    1: ("Bulb", 9),
    2: ("Light", 10),
    4: ("Motor", 11)
}

# Initialize pin objects
led_pins = {finger: board.get_pin(f'd:{pin}:o') for finger, (_, pin) in device_map.items()}

# Hand detector setup
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Video capture setup
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)

    hands, img = detector.findHands(frame)

    if hands:
        hand = hands[0]
        fingerUp = detector.fingersUp(hand)

        y_offset = 60
        for finger_index, (label, _) in device_map.items():
            status = "ON" if fingerUp[finger_index] else "OFF"
            led_pins[finger_index].write(0 if fingerUp[finger_index] else 1)

            color = (0, 255, 0) if status == "ON" else (0, 0, 255)
            cv2.putText(frame, f'{label}: {status}', (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            y_offset += 40

        # Display total finger count
        finger_count = sum([fingerUp[i] for i in device_map.keys()])
        cv2.putText(frame, f'Fingers Up: {finger_count}', (20, 300),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) == ord('k'):
        break

video.release()
cv2.destroyAllWindows()
