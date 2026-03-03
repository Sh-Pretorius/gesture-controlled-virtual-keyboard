# Touchless Desk: a Gesture Controlled Virtual Keyboard :desktop_computer::raised_hand_with_fingers_splayed:
## :ledger:Table of Contents
1. Project Introduction
2. Project Overview and Features
3. Tech Stack
4. Techinical Features
5. Getting Started
6. Architecture
7. Skills Demonstrated

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
