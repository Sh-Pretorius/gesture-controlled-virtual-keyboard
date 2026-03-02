import json
import os

class MouseCalibration:
    def __init__(self, file_path="calibration.json"):
        self.file_path = file_path

        # Calibration state
        self.calibrating = False
        self.calibration_step = 0

        # Default full-frame calibration
        self.calib_x_min = 0.0
        self.calib_y_min = 0.0
        self.calib_x_max = 1.0
        self.calib_y_max = 1.0

    # Start calibration process
    def start(self):
        self.calibrating = True
        self.calibration_step = 1
        print("Calibration started.")
        print("Move finger to TOP-LEFT and press C.")

    # Handle calibration steps
    def handle(self, hands):
        """
        Sets up and handles the calibration steps so user knows when to do what
        """
        if not self.calibrating:
            return

        if not hands or not hands.hand_landmarks:
            return

        hand_landmarks = hands.hand_landmarks[0]
        index_tip = hand_landmarks[8]

        # Save TOP-LEFT
        if self.calibration_step == 1:
            self.calib_x_min = index_tip.x
            self.calib_y_min = index_tip.y
            print("Top-left saved.")
            print("Move finger to BOTTOM-RIGHT and press C.")
            self.calibration_step = 2

        # Save BOTTOM-RIGHT
        elif self.calibration_step == 2:
            self.calib_x_max = index_tip.x
            self.calib_y_max = index_tip.y

            # Ensure correct ordering
            self.calib_x_min, self.calib_x_max = sorted(
                [self.calib_x_min, self.calib_x_max]
            )
            self.calib_y_min, self.calib_y_max = sorted(
                [self.calib_y_min, self.calib_y_max]
            )

            print("Calibration complete.")
            self.save()

            self.calibrating = False
            self.calibration_step = 0

    # Save calibration to file
    def save(self):
        """
        Saves the calibration data to file
        """
        data = {
            "calib_x_min": self.calib_x_min,
            "calib_y_min": self.calib_y_min,
            "calib_x_max": self.calib_x_max,
            "calib_y_max": self.calib_y_max
        }

        with open(self.file_path, "w") as f:
            json.dump(data, f)

        print("Calibration saved.")

    # Load calibration from file
    def load(self):
        """
        If a calibration.json file exists, it loads the data saved on it
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)

            self.calib_x_min = data["calib_x_min"]
            self.calib_y_min = data["calib_y_min"]
            self.calib_x_max = data["calib_x_max"]
            self.calib_y_max = data["calib_y_max"]

            print("Calibration loaded.")
        else:
            print("No calibration file found.")

    # Apply calibrated mapping
    def apply(self, x, y):
        """
        Takes normalized landmark coordinates (0–1)
        Returns calibrated normalized coordinates
        """

        if (self.calib_x_max - self.calib_x_min == 0 or
                self.calib_y_max - self.calib_y_min == 0):
            return x, y

        x = (x - self.calib_x_min) / (self.calib_x_max - self.calib_x_min)
        y = (y - self.calib_y_min) / (self.calib_y_max - self.calib_y_min)

        x = max(0, min(x, 1))
        y = max(0, min(y, 1))

        return x, y