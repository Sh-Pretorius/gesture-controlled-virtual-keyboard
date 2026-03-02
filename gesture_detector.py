import json
import time
import ctypes
import math

# Windows API Setup
user32 = ctypes.windll.user32

# Load Gesture Mapping JSON
with open("key_gesture_layout.json", "r") as f:
    gesture_map = json.load(f)

# Global State Variables
typing_mode = False
last_output_time = 0
cooldown = 0.6

# Hold confirmation
hold_time_required = 0.4
gesture_start_time = None
stable_digit = None
gesture_confirmed = False
gesture_confirm_time = None
static_timeout = 0.6  # seconds after hold (0.4 if its too slow)

# Swipe buffer
position_buffer = []
buffer_size = 10

# Distance Between Two Landmarks
def distance(p1, p2):
    """
    A helper for calculating the distance between two hand landmarks
    """
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )

# Thumb Detection (Handedness Aware)
def is_thumb_extended(hand_landmarks, handedness):
    """
    Diffirentiates whether the thumb is on the left or right hand
    """

    if handedness == "Right":
        return hand_landmarks[4].x > hand_landmarks[3].x
    else:  # Left hand
        return hand_landmarks[4].x < hand_landmarks[3].x

# Digit Detection
def get_digit(hands):
    """
    Detects what digit is being used
    returns the detected digit 
    """

    if not hands.hand_landmarks:
        return None

    hand_landmarks = hands.hand_landmarks[0]
    handedness = hands.handedness[0][0].category_name

    fingers = []

    # Thumb
    fingers.append(is_thumb_extended(hand_landmarks, handedness))

    # Index
    fingers.append(hand_landmarks[8].y < hand_landmarks[6].y)

    # Middle
    fingers.append(hand_landmarks[12].y < hand_landmarks[10].y)

    # Ring
    fingers.append(hand_landmarks[16].y < hand_landmarks[14].y)

    # Pinky
    fingers.append(hand_landmarks[20].y < hand_landmarks[18].y)

    # Digit 9 (Pinch)
    if distance(hand_landmarks[4], hand_landmarks[8]) < 0.03:
        return 9

    # Pattern Matching
    if fingers == [
        False,  # thumb down
        True,   # index up
        False,  # middle down
        False,  # ring down
        False   # pinky down
        ]:
        return 1
    if fingers == [
        False,  # thumb down 
        True,   # index up
        True,   # middle up
        False,  # ring down
        False   # pinky down
        ]:
        return 2
    if fingers == [
        False,  # thumb down 
        True,   # index up
        True,   # middle up
        True,   # ring up
        False   # pinky down
        ]:
        return 3
    if fingers == [
        False,  # thumb down 
        True,   # index up
        True,   # middle up 
        True,   # ring up
        True    # pinky up
        ]:
        return 4
    if fingers == [
        True,   # thumb up
        True,   # index up 
        True,   # middle up
        True,   # ring up
        True    # pinky up
        ]:
        return 5
    if fingers == [
        True,   # thumb up 
        False,  # index down
        False,  # middle down
        False,  # ring down
        False   # pinky down
        ]:
        return 6
    if fingers == [
        False,  # thumb down
        False,  # index down
        False,  # middle down
        False,  # ring down
        True    # pinky up
        ]:
        return 7
    if fingers == [
        True,   # thumb up
        False,  # index down
        False,  # middle down
        False,  # ring down
        True    # pinky up
        ]:
        return 8
    if fingers == [
        False,  # thumb down
        False,  # index down
        False,  # middle down
        False,  # ring down
        False   # pinky down
        ]:
        return 0

    return None

# Swipe Detection (10 Frame Buffer)
def get_direction(hands):
    """
    Detects the direction of movement or whether movement is static.
    """

    global position_buffer

    hand_landmarks = hands.hand_landmarks[0]
    index_tip = hand_landmarks[8]

    current_pos = (index_tip.x, index_tip.y)
    position_buffer.append(current_pos)

    if len(position_buffer) > buffer_size:
        position_buffer.pop(0)

    if len(position_buffer) < buffer_size:
        return "STATIC"

    start_x, start_y = position_buffer[0]
    end_x, end_y = position_buffer[-1]

    dx = end_x - start_x
    dy = end_y - start_y

    threshold = 0.08

    if abs(dx) > abs(dy):
        if abs(dx) > threshold:
            return "RIGHT" if dx > 0 else "LEFT"
    else:
        if abs(dy) > threshold:
            return "DOWN" if dy > 0 else "UP"

    return "STATIC"

# Main Gesture Processor
def process_gesture(hands):
    """
    Detects hand, digit, and movement and maps it to corresponding key + gesture map
    """

    global typing_mode
    global last_output_time
    global gesture_start_time
    global stable_digit
    global position_buffer
    global gesture_confirmed
    global gesture_confirm_time
    global static_timeout

    # No hand detected -> reset
    if not hands or not hands.hand_landmarks:
        gesture_start_time = None
        stable_digit = None
        gesture_confirmed = False
        position_buffer.clear()
        return None

    current_time = time.time()
    digit = get_digit(hands)

    if digit is None:
        gesture_start_time = None
        stable_digit = None
        gesture_confirmed = False
        position_buffer.clear()
        return None

    # Stage 1 — Hold Confirmation
    if not gesture_confirmed:

        if stable_digit != digit:
            stable_digit = digit
            gesture_start_time = current_time
            return None

        if current_time - gesture_start_time < hold_time_required:
            return None

        gesture_confirmed = True
        gesture_confirm_time = current_time
        position_buffer.clear()
        return None

    # Stage 2 — Swipe detection or Static
    direction = get_direction(hands)

    # Swipe detected
    if direction != "STATIC":

        key = f"{digit}_{direction}"

        if key in gesture_map and (current_time - last_output_time > cooldown):

            last_output_time = current_time
            output = gesture_map[key]

            # Mode switch
            if output == "Mode switch":
                typing_mode = not typing_mode
                print("Typing Mode:", typing_mode)

            # Reset
            gesture_confirmed = False
            stable_digit = None
            gesture_start_time = None
            gesture_confirm_time = None
            position_buffer.clear()

            if output == "Mode switch":
                return None

            return output

    # Static timeout
    if current_time - gesture_confirm_time > static_timeout:

        key = f"{digit}_STATIC"

        if key in gesture_map and (current_time - last_output_time > cooldown):

            last_output_time = current_time
            output = gesture_map[key]

            # Mode switch
            if output == "Mode switch":
                typing_mode = not typing_mode
                print("Typing Mode:", typing_mode)

            # Reset
            gesture_confirmed = False
            stable_digit = None
            gesture_start_time = None
            gesture_confirm_time = None
            position_buffer.clear()

            if output == "Mode switch":
                return None

            return output

    return None

# OS Typing Function
def type_character(char):

    VK_CODE = {
        "SPACE": 0x20,
        "ENTER": 0x0D,
        "BACKSPACE": 0x08
    }

    if char in VK_CODE:
        vk = VK_CODE[char]
    else:
        vk = ord(char.upper())

    # Key press
    user32.keybd_event(vk, 0, 0, 0)
    # Key release
    user32.keybd_event(vk, 0, 2, 0)