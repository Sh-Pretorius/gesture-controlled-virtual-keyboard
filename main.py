import cv2
import time
import gesture_detector as gd
import mediapipe as mp
import mouse_callibration as mc
from mouse_callibration import MouseCalibration
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mouse_controller import move_mouse, map_to_screen, smooth_move_mouse
from mouse_controller import OneEuroFilter
from mouse_controller import mouse_down, mouse_up

# Global variables
x_landmark_filter = OneEuroFilter(min_cutoff=1.7, beta=0.01)
y_landmark_filter = OneEuroFilter(min_cutoff=1.7, beta=0.01)
is_dragging = False

# Camera function
def start_camera():
    """
    Starts web camera.
    Returns a camera object
    """
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("start_camera func: Failed to launch Camera")
        exit()
    print("Camera is active")   # Successfully started webcam
    return camera

# Hand tracker function
def initialize_hand_tracker(
    model_path: str = "hand_landmarker.task",
    num_hands = 1,
    running_mode = vision.RunningMode.VIDEO,
    min_hand_detection_confidence = 0.7,
    min_tracking_confidence = 0.7
    ):
    """
    Sets up Mediapipe Handlandmaker function. Contains configuration options for Handlandmaker object. Returns the function to detect hands and 21 landmarks on the hand.
    """

    base_options = python.BaseOptions(model_asset_path = model_path)

    # Hand tracker tuning options
    options = vision.HandLandmarkerOptions(
        base_options = base_options,
        num_hands = num_hands,  # Only read one hand at a time
        running_mode = running_mode,
        min_hand_detection_confidence = min_hand_detection_confidence,  # Discards poor hand detection and reduces false positives
        min_tracking_confidence = min_tracking_confidence # Ensures poor landmark tracking is ignored
    )
    return vision.HandLandmarker.create_from_options(options)

# Draw hand landmarks function
def draw_hand_landmarks(frame, hands):
    """
    This function loops through the detected hands and converts normalized coordinates to pixels. 
    Draws a green circle over each detected landmark
    """

    if hands.hand_landmarks:

        for hand_landmarks in hands.hand_landmarks:
            height, width, _ = frame.shape

            # Draw landmarks (Green circles)
            for landmark in hand_landmarks:
                current_x, current_y = int(landmark.x * width), int(landmark.y * height)
                cv2.circle(frame, (current_x, current_y), 5, (0, 255, 0), -1)

# Move mouse cursor function
def control_mouse(frame, hands, calibration):
    """
    Moves mouse using index fingertip
    """

    if hands.hand_landmarks:
        height, width, _ = frame.shape

        for hand_landmarks in hands.hand_landmarks:

            middle_index = hand_landmarks[12]

            # Reduce landmark jitters -> less mouse jitter
            filtered_x = x_landmark_filter.filter(middle_index.x, time.time())
            filtered_y = y_landmark_filter.filter(middle_index.y, time.time())

            calibrated_x, calibrated_y = calibration.apply(
                filtered_x,
                filtered_y
            )

            frame_x = int(calibrated_x * width)
            frame_y = int(calibrated_y * height)

            screen_x, screen_y = map_to_screen(frame_x, frame_y, width, height)

            smooth_move_mouse(screen_x, screen_y) 

# pinch helper
def is_pinch(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    index_tip = hand_landmarks[8]

    distance = ((thumb_tip.x - index_tip.x) ** 2 +
                (thumb_tip.y - index_tip.y) ** 2) ** 0.5

    return distance < 0.03   

# MAIN function
def main():
    """
    Main function that calls the other functions.
    """

    # Initialize required models and variables
    camera = start_camera() # Start camera
    hand_tracker = initialize_hand_tracker()    # Get landmark points for hand 
    start_time = time.time()
    calibration = MouseCalibration()
    calibration.load()
    global is_dragging

    while True:
        flag, frame = camera.read()
        if not flag:
            print("Main func: Can't receive frame") # flag = false and the frame was not captured
            break

        # Visual video operations
        frame = cv2.flip(frame, 1)  # Mirror video feed
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # Re-color frame to RGB for mp processing

        # Hand tracking operations
        mp_image = mp.Image(
            image_format = mp.ImageFormat.SRGB,
            data = rgb_frame
            )
        timestamp = int((time.time() - start_time) * 1000)
        hands = hand_tracker.detect_for_video(mp_image, timestamp)

        # Draw hand landmarks and skeleton
        draw_hand_landmarks(frame, hands)

        # Gestures
        char = gd.process_gesture(hands)

        # Typing mode
        if gd.typing_mode and char:
            print("Detected:", char)
            gd.type_character(char)

        # Mouse mode
        if not gd.typing_mode and hands.hand_landmarks:

            control_mouse(frame, hands, calibration)

            hand_landmarks = hands.hand_landmarks[0]
            pinch = is_pinch(hand_landmarks) and not gd.typing_mode

            # Pinch started → Mouse Down
            if pinch and not is_dragging:
                mouse_down("left")
                is_dragging = True
                print("Drag Start")

            # Pinch released → Mouse Up
            elif not pinch and is_dragging:
                mouse_up("left")
                is_dragging = False
                print("Drag End")

        # Display video
        cv2.imshow("Hand Tracking", frame)

        # Key commands
        pressed_key = cv2.waitKey(1) & 0xFF

        if pressed_key == ord("c"):
            if not calibration.calibrating:
                calibration.start()
            else:
                calibration.handle(hands)

        # Close program
        if pressed_key == 27:   # Escape key
            break

    # Cleanup
    camera.release()
    cv2.destroyAllWindows()

main()