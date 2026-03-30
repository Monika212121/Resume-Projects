# Aim: Define colors of the bounding boxes.

# These colours are according to the TrackedState of an object

STATUS_COLORS = {
    "new": (255, 255, 255),             # WHITE
    "stable": (255, 255, 255),          # WHITE
    "selected": (0, 165, 255),          # ORANGE
    "unattempted": (255, 0, 255),       # MAJENTA
    "collected": (0, 255, 0),           # GREEN
    "lost": (0, 0, 255),                # RED
    "ignored": (255, 255, 0),           # CYAN
    "avoided": (0, 255, 255)            # Bright Fluorescent Yellow (BGR for OpenCV)
}