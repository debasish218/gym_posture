"""Configuration for posture alignment application."""

# Alignment thresholds (in degrees for angles, normalized units for positions)
ALIGNMENT_THRESHOLDS = {
    "green": 15.0,      # Error <= 15 degrees/units = green
    "yellow": 30.0,     # Error <= 30 degrees/units = yellow
    "red": 100.0        # Error > 30 = red
}

# Colors for visualization (BGR format for OpenCV)
COLORS = {
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "red": (0, 0, 255),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "reference": (200, 200, 200),  # Light gray for reference pose
    "live": (100, 200, 255)        # Light blue for live pose
}

# Joint connection pairs for skeleton visualization
SKELETON_CONNECTIONS = [
    # Head and neck
    (0, 1),    # Nose to left eye
    (1, 2),    # Left eye to right eye
    (2, 0),    # Right eye to nose
    (0, 3),    # Nose to left ear
    (0, 4),    # Nose to right ear

    # Upper body
    (5, 6),    # Left shoulder to right shoulder
    (5, 7),    # Left shoulder to left elbow
    (7, 9),    # Left elbow to left wrist
    (6, 8),    # Right shoulder to right elbow
    (8, 10),   # Right elbow to right wrist

    # Torso
    (5, 11),   # Left shoulder to left hip
    (6, 12),   # Right shoulder to right hip
    (11, 12),  # Left hip to right hip

    # Lower body
    (11, 13),  # Left hip to left knee
    (13, 15),  # Left knee to left ankle
    (12, 14),  # Right hip to right knee
    (14, 16),  # Right knee to right ankle
]

# Important joints for alignment checking
ALIGNMENT_JOINTS = {
    "left_shoulder": 5,
    "right_shoulder": 6,
    "left_elbow": 7,
    "right_elbow": 8,
    "left_hip": 11,
    "right_hip": 12,
    "left_knee": 13,
    "right_knee": 14,
    "left_ankle": 15,
    "right_ankle": 16,
}

# Angle-based joints (for joint angle comparison)
ANGLE_JOINTS = {
    "left_elbow": (5, 7, 9),        # Left shoulder, elbow, wrist
    "right_elbow": (6, 8, 10),      # Right shoulder, elbow, wrist
    "left_knee": (11, 13, 15),      # Left hip, knee, ankle
    "right_knee": (12, 14, 16),     # Right hip, knee, ankle
}

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# Display settings
FONT = __import__('cv2').FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1.0
FONT_THICKNESS = 2
JOINT_RADIUS = 6
SKELETON_THICKNESS = 2

# Confidence threshold for MediaPipe detections
CONFIDENCE_THRESHOLD = 0.5

# Overlay transparency for reference pose
REFERENCE_ALPHA = 0.4
