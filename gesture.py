import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]

def get_finger_states(landmarks):
    fingers = []
    # Thumb: compare x
    fingers.append(landmarks[4].x < landmarks[3].x)
    # Other 4 fingers: tip y above pip y = extended
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        fingers.append(landmarks[tip].y < landmarks[pip].y)
    return fingers

def classify_gesture(landmarks):
    fingers = get_finger_states(landmarks)
    extended = sum(fingers)

    if extended == 0:
        return "rock"
    if extended == 5:
        return "paper"
    if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
        return "scissors"
    return None

def test_gesture():
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7
    )
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    print("Show Rock / Paper / Scissors. Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_image)

        gesture = None
        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            gesture = classify_gesture(landmarks)

            # Draw landmarks
            h, w = frame.shape[:2]
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        label = gesture.upper() if gesture else "..."
        cv2.putText(frame, label, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 255, 0), 3)
        cv2.imshow("Gesture Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_gesture()