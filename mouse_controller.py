import ctypes
import math
import time

# Windows API Setup
user32 = ctypes.windll.user32

# 1€ Filter Algrithm (https://jaantollander.com/post/noise-filtering-using-one-euro-filter/#tuning-the-filter | https://gery.casiez.net/1euro/)
class OneEuroFilter:
    def __init__(self, min_cutoff=1.6, beta=0.015, d_cutoff=1.0):
        """
        Adaptive low-pass filter that reduces jitter during slow movement and increases responsiveness during fast movement using velocity-based dynamic smoothing.
        """
        # Parameters
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        # Previous values
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def alpha(self, cutoff, dt):
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def filter(self, x, t):
        if self.t_prev is None:
            self.t_prev = t
            self.x_prev = x
            return x

        dt = t - self.t_prev
        self.t_prev = t

        if dt <= 0.0:
            return x

        # The filtered derivative
        dx = (x - self.x_prev) / dt
        alpha_d = self.alpha(self.d_cutoff, dt)
        dx_hat = alpha_d * dx + (1 - alpha_d) * self.dx_prev

        # Adaptive cutoff
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        # Filtered value
        alpha = self.alpha(cutoff, dt)
        x_hat = alpha * x + (1 - alpha) * self.x_prev

        self.x_prev = x_hat
        self.dx_prev = dx_hat

        return x_hat

# Screen Utilities Functions
def get_screen_size():
    """ 
    Returns screen width and height 
    """
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width, screen_height

def move_mouse(pos_x, pos_y):
    """ 
    Moves mouse cursor to (x, y) screen coordinates 
    """
    user32.SetCursorPos(int(pos_x), int(pos_y))

def map_to_screen(frame_x, frame_y, frame_width, frame_height):
    """ 
    Maps camera frame coordinates to full screen coordinates 
    """
    screen_width, screen_height = get_screen_size()

    screen_x = (frame_x / frame_width) * screen_width
    screen_y = (frame_y / frame_height) * screen_height

    return screen_x, screen_y

# Global filters
x_filter = OneEuroFilter(min_cutoff=1.2, beta=0.02)
y_filter = OneEuroFilter(min_cutoff=1.2, beta=0.02)
prev_time = time.time()

# Mouse Smoothing Controller Function
def smooth_move_mouse(target_x, target_y):
    """ 
    Applies dynamic smoothing based on speed of the hand before moving mouse 
    """
    global prev_time

    current_time = time.time()
    prev_time = current_time
    
    filtered_x = x_filter.filter(target_x, current_time)
    filtered_y = y_filter.filter(target_y, current_time)

    move_mouse(filtered_x, filtered_y)

# left button hold
def mouse_down(button = "left"):
    if button == "left":
        user32.mouse_event(0x0002, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(0x0008, 0, 0, 0)

# left button release
def mouse_up(button="left"):
    if button == "left":
        user32.mouse_event(0x0004, 0, 0, 0)
    elif button == "right":
        user32.mouse_event(0x0010, 0, 0, 0, 0)