"""
Example: How to Add a New Exercise (Squat)

This file demonstrates how to extend the application to support
a new exercise. Copy patterns from here to add more exercises.

To use this:
1. Uncomment imports at the top of reference_pose.py
2. Import SquatReferencePose in main.py
3. Add exercise selection to main.py
"""

import numpy as np
from reference_pose import ReferencePose


class SquatReferencePose(ReferencePose):
    """Reference pose for squat exercise at bottom position."""

    def __init__(self):
        """Initialize squat reference pose."""
        landmarks = self._create_squat_pose()
        super().__init__(landmarks=landmarks, name="squat_bottom")

    def _create_squat_pose(self):
        """
        Create a squat pose at the bottom position.

        Squat characteristics:
        - Knees bent ~90 degrees
        - Shins relatively vertical
        - Torso upright (minimal forward lean)
        - Hips below knees
        - Weight in heels
        """
        pose = np.zeros((33, 3))

        # Head and eyes (same as standing)
        pose[0] = [0.0, -0.5, 0.0]     # Nose
        pose[1] = [-0.05, -0.55, 0.0]  # Left eye
        pose[2] = [0.05, -0.55, 0.0]   # Right eye
        pose[3] = [-0.1, -0.5, 0.0]    # Left ear
        pose[4] = [0.1, -0.5, 0.0]     # Right ear

        # Shoulders (pulled back slightly, chest up)
        pose[5] = [-0.15, -0.15, 0.0]  # Left shoulder
        pose[6] = [0.15, -0.15, 0.0]   # Right shoulder

        # Elbows (bent, bringing hands forward for balance)
        pose[7] = [-0.1, 0.05, 0.0]    # Left elbow
        pose[8] = [0.1, 0.05, 0.0]     # Right elbow

        # Wrists (in front of body, arms bent)
        pose[9] = [-0.1, 0.15, 0.0]    # Left wrist
        pose[10] = [0.1, 0.15, 0.0]    # Right wrist

        # Hips (much lower, ~45% down)
        pose[11] = [-0.1, 0.25, 0.0]   # Left hip
        pose[12] = [0.1, 0.25, 0.0]    # Right hip

        # Knees (bent, roughly 90 degrees)
        pose[13] = [-0.1, 0.50, 0.0]   # Left knee
        pose[14] = [0.1, 0.50, 0.0]    # Right knee

        # Ankles (feet on ground, shins vertical)
        pose[15] = [-0.1, 0.75, 0.0]   # Left ankle
        pose[16] = [0.1, 0.75, 0.0]    # Right ankle

        # Other landmarks
        for i in range(17, 33):
            pose[i] = pose[i - 17] if i < 25 else [0.0, 0.0, 0.0]

        return pose


class LungeReferencePose(ReferencePose):
    """Reference pose for lunge exercise."""

    def __init__(self, side="right"):
        """
        Initialize lunge reference pose.

        Args:
            side: "right" or "left" for which leg is forward
        """
        landmarks = self._create_lunge_pose(side)
        super().__init__(landmarks=landmarks, name=f"lunge_{side}")
        self.side = side

    def _create_lunge_pose(self, side="right"):
        """
        Create a lunge pose.

        Lunge characteristics:
        - Front knee bent ~90 degrees
        - Back knee lowered close to ground
        - Torso upright
        - Front foot forward
        - Back heel raised
        """
        pose = np.zeros((33, 3))

        # Head (same)
        pose[0] = [0.0, -0.5, 0.0]

        # Shoulders (neutral)
        pose[5] = [-0.15, -0.2, 0.0]
        pose[6] = [0.15, -0.2, 0.0]

        # Elbows
        pose[7] = [-0.15, 0.0, 0.0]
        pose[8] = [0.15, 0.0, 0.0]

        # Wrists
        pose[9] = [-0.15, 0.2, 0.0]
        pose[10] = [0.15, 0.2, 0.0]

        # Hips (shifted based on side)
        if side == "right":
            pose[11] = [-0.05, 0.3, 0.0]  # Left hip
            pose[12] = [0.15, 0.3, 0.0]   # Right hip (forward)
        else:
            pose[11] = [-0.15, 0.3, 0.0]  # Left hip (forward)
            pose[12] = [0.05, 0.3, 0.0]   # Right hip

        # Knees (front bent, back high)
        if side == "right":
            pose[13] = [-0.05, 0.55, 0.0]  # Left knee (back, high)
            pose[14] = [0.15, 0.5, 0.0]    # Right knee (front, bent)
        else:
            pose[13] = [-0.15, 0.5, 0.0]   # Left knee (front, bent)
            pose[14] = [0.05, 0.55, 0.0]   # Right knee (back, high)

        # Ankles
        if side == "right":
            pose[15] = [-0.05, 0.8, 0.0]   # Left ankle (back)
            pose[16] = [0.15, 0.75, 0.0]   # Right ankle (front)
        else:
            pose[15] = [-0.15, 0.75, 0.0]  # Left ankle (front)
            pose[16] = [0.05, 0.8, 0.0]    # Right ankle (back)

        return pose


class DeadliftReferencePose(ReferencePose):
    """Reference pose for deadlift at bottom position."""

    def __init__(self):
        """Initialize deadlift reference pose."""
        landmarks = self._create_deadlift_pose()
        super().__init__(landmarks=landmarks, name="deadlift_bottom")

    def _create_deadlift_pose(self):
        """
        Create a deadlift pose at setup/bottom position.

        Deadlift characteristics:
        - Hips higher than in squat
        - Knees slightly bent
        - Flat back, shoulders over bar
        - Head neutral
        - Arms straight
        """
        pose = np.zeros((33, 3))

        # Head (neutral, eyes forward)
        pose[0] = [0.0, -0.5, 0.0]

        # Shoulders (directly over hips, arms straight)
        pose[5] = [-0.15, -0.05, 0.0]
        pose[6] = [0.15, -0.05, 0.0]

        # Elbows (straight, locked)
        pose[7] = [-0.15, 0.2, 0.0]
        pose[8] = [0.15, 0.2, 0.0]

        # Wrists (straight, neutral)
        pose[9] = [-0.15, 0.35, 0.0]
        pose[10] = [0.15, 0.35, 0.0]

        # Hips (higher, ~40% down)
        pose[11] = [-0.1, 0.35, 0.0]
        pose[12] = [0.1, 0.35, 0.0]

        # Knees (slightly bent)
        pose[13] = [-0.1, 0.55, 0.0]
        pose[14] = [0.1, 0.55, 0.0]

        # Ankles
        pose[15] = [-0.1, 0.75, 0.0]
        pose[16] = [0.1, 0.75, 0.0]

        return pose


# Example: How to integrate into main.py

def example_main_py_extension():
    """
    Example code to add to main.py for exercise selection.

    In PostureAlignmentApp.__init__():

    def __init__(self):
        self.cap = None
        self.pose_detector = None
        self.reference_pose = None
        self.frame_count = 0
        self.current_alignment = None

        # NEW: Exercise management
        self.exercise = "upright"
        self.available_exercises = {
            "upright": ReferencePose(),
            "squat": SquatReferencePose(),
            "lunge_right": LungeReferencePose("right"),
            "lunge_left": LungeReferencePose("left"),
            "deadlift": DeadliftReferencePose(),
        }

    Then in run():

    while True:
        # ... existing code ...

        # NEW: Handle number keys to switch exercises
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            self.exercise = "upright"
            self.reference_pose = self.available_exercises["upright"]
        elif key == ord('2'):
            self.exercise = "squat"
            self.reference_pose = self.available_exercises["squat"]
        elif key == ord('3'):
            self.exercise = "lunge_right"
            self.reference_pose = self.available_exercises["lunge_right"]
        # ... etc
    """
    pass


# Example: How to add exercise-specific feedback

def example_feedback_py_extension():
    """
    Example code to add to feedback.py for exercise-specific messages.

    EXERCISE_SPECIFIC_CORRECTIONS = {
        "squat": {
            "left_knee": "Keep your left knee tracking over your toes",
            "right_knee": "Keep your right knee tracking over your toes",
            "torso": "Keep your chest up, don't lean forward excessively",
            "left_ankle": "Keep your weight in your heels",
            "right_ankle": "Keep your weight in your heels",
        },
        "lunge": {
            "front_knee": "Keep your front knee over your ankle",
            "back_knee": "Lower your back knee closer to the ground",
            "torso": "Keep your torso upright",
        },
        "deadlift": {
            "torso": "Keep your back flat, shoulders over the bar",
            "left_knee": "Push through your heels",
            "right_knee": "Push through your heels",
        },
    }

    def generate_exercise_feedback(alignment_result, exercise):
        corrections = EXERCISE_SPECIFIC_CORRECTIONS.get(exercise, {})
        # ... use corrections to generate better messages
    """
    pass


if __name__ == "__main__":
    # Test creating poses
    print("Testing exercise reference poses...\n")

    poses = {
        "upright": ReferencePose(),
        "squat": SquatReferencePose(),
        "lunge_right": LungeReferencePose("right"),
        "lunge_left": LungeReferencePose("left"),
        "deadlift": DeadliftReferencePose(),
    }

    for name, pose in poses.items():
        print(f"✓ Created {name:20} | Shape: {pose.landmarks.shape}")

    print("\n✓ All exercise poses created successfully!")
    print("\nTo use these, add to reference_pose.py and import in main.py")
