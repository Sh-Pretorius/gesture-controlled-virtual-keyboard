# Touchless Desk: a Gesture Controlled Virtual Keyboard :desktop_computer::raised_hand_with_fingers_splayed:
## :ledger:Table of Contents
1. Project Introduction
2. Project Overview and Features
3. Tech Stack
4. Techinical Features
5. Getting Started
6. Architecture
7. Skills Demonstrated
8. Hand Gesture Guide

## 1. Project Introduction
Built a real-time computer vision system that converts hand gestures into mouse and keyboard input, enabling fully touchless interaction with a Windows computer using only a webcam. Implemented adaptive One Euro filtering to reduce jitter and designed a two-stage gesture confirmation engine to prevent false triggers.

Enables touchless computer interaction. Users control mouse and keyboard functions without touching hardware. Useful in situaions where hands are dirty, occupied, or with public/shared devices.

## 2. Features
- Control the mouse using hand movement
- Type using digit-based gesture recognition
- Switch between mouse mode and typing mode
- Perform OS-level keyboard and mouse control

## 3. Tech Stack
- MediaPipe
- OpenCV
- Python
- Windows API
- Signal Processing
- JSON-based Configuration

## 4. Techinical Features
- 21 landmark real-time hand tracking
- Digit detection using finger state logic
- Hold-confirmation gesture system
- Swipe direction detection using 10-frame buffer
- One Euro Filter smoothing algorithm
- Customizable gesture-to-key mapping
- Mouse calibration system
- Pinch-to-drag support

## 5. Getting Started
- How to Run
  - pip install -r requirements.txt
  - python main.py
- Modes
  - Mouse Mode
  - Move mouse with index finger
  - Pinch to drag
  - Real-time smoothing
- Typing Mode
  - Show digit (1–9)
  - Hold to confirm
  - Swipe or stay static
  - Character output mapped from JSON
    
## 6. Architecture
A modular, pipeline-based architecture with state-driven control.
- main.py → Main program loop
- gesture_detector.py → Gesture recognition logic
- mouse_controller.py → Mouse smoothing & OS control
- mouse_callibration.py → Calibration system
- key_gesture_layout.json → Custom gesture mapping

## 7. Skills Demonstrated
- Computer Vision
- Signal Processing
- Real-Time Systems
- State Machines
- OS-level Input Control
- Algorithm Design

## 8. Hand Gesture Guide
The digit + swipe system works by first figuring out which number you’re showing using hand landmarks from MediaPipe. It checks which fingers are up or down to determine a digit from 0–9. To avoid accidental inputs, the digit has to stay steady for a short moment before it’s confirmed. After that, the system watches how your fingertip moves over a few frames to detect a direction like left, right, down, or if you keep it still. That digit and direction combo (for example, 1 + RIGHT) creates a unique key that’s matched in a JSON file to a letter or action. When designing the JSON layout, I looked at English letter frequency and assigned the most common letters — like E, T, A, O, I, and N — to the easiest gestures, usually lower digits with little or no movement. The idea was to reduce hand fatigue and make typing feel more natural and efficient over time. 

### 🫰 Basic Gestures
- :fist: **Digit 0:** Fist *(All fingers are folded)*
- ☝️ **Digit 1:** Index Only *(Index finger extended, all others folded.)*
- :v: **Digit 2:** Index and Middle *(Index and Middle extended, all others folded.)*
- :warning: **Digit 3:** Index, Middle, and Ring *(Index, Middle, and Ring fingers extended, all others folded.)*
- :warning: **Digit 4:** All except thumb *(Index, Middle, Ring, and Pinky extended, thumb folded)*
- :raised_hand: **Digit 5:** All *(All extended, no folded fingers.)*
- :thumbsup: **Digit 6:** Thumb only *(Thumb extended, others folded.)*
- :warning: **Digit 7:** Pinky only *(Pinky extended, others folded.)*
- :call_me_hand: **Digit 8:** Thumb and Pinky extended *(Pinky and thumb extended, others folded)*
- :pinching_hand: **Digit 9:** Thumb and Index TOUCHING (pinch) *(Thumb tip very close to index tip, others folded)*

### ⤵️ Swipe direction
- *️⃣**Static:** Hold the gesture/digit still *(S)*
- ➡️**Right** Swipe your hand right *(R)*
- ⬅️**Left** Swipe your hand left *(L)*
- ⬇️**DOWN** Swipe your hand down *(D)*

### Gesture Alphabet
| Digit + Swipe  | Alphabet letter |
| ------------- | -------------|
| 1 - S | E |
| 1 - R | T |
| 1 - L | A |
| 1 - D | O |
| 2 - S | I |
| 2 - R | N |
| 2 - L | R |
| 2 - D | S |
| 3 - S | H |
| 3 - R | L |
| 3 - L | D |
| 3 - D | C |
| 4 - S | U |
| 4 - R | M |
| 4 - L | F |
| 4 - D | P |
| 5 - S | G |
| 5 - R | W |
| 5 - L | Y |
| 5 - D | B |
| 6 - S | V |
| 6 - R | K |
| 6 - L | J |
| 6 - D | X |
| 7 - S | Q |
| 7 - R | Z |
| 9 - S | Space |
| 9 - R | Backspace |
| 9 - L | Enter |
| 8 - S |Mode switch |
