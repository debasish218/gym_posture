"""Reference pose management."""

import numpy as np
from config import ALIGNMENT_JOINTS, ANGLE_JOINTS


class ReferencePose:
    """Manages reference poses for alignment checking."""

    def __init__(self, landmarks=None, name="default"):
        """
        Initialize reference pose.

        Args:
            landmarks: numpy array of shape (33, 3) with normalized landmarks
            name: name of the reference pose (e.g., "upright", "squat", etc.)
        """
        self.name = name
        if landmarks is None:
            self.landmarks = self._create_default_upright_pose()
        else:
            self.landmarks = landmarks

    def _create_default_upright_pose(self):
        """
        Create a default upright standing posture.

        Returns:
            numpy array of shape (33, 3) with normalized landmarks
        """
        # Create a standing pose with normalized coordinates
        # Scale is approximately 1.0 for body width, body centered
        pose = np.zeros((33, 3))

        # Head and eyes (roughly centered at top)
        pose[0] = [0.0, -0.5, 0.0]   # Nose
        pose[1] = [-0.05, -0.55, 0.0]  # Left eye
        pose[2] = [0.05, -0.55, 0.0]   # Right eye
        pose[3] = [-0.1, -0.5, 0.0]    # Left ear
        pose[4] = [0.1, -0.5, 0.0]     # Right ear

        # Shoulders
        pose[5] = [-0.15, -0.2, 0.0]   # Left shoulder
        pose[6] = [0.15, -0.2, 0.0]    # Right shoulder

        # Elbows (slightly out)
        pose[7] = [-0.15, 0.0, 0.0]    # Left elbow
        pose[8] = [0.15, 0.0, 0.0]     # Right elbow

        # Wrists (at sides)
        pose[9] = [-0.15, 0.2, 0.0]    # Left wrist
        pose[10] = [0.15, 0.2, 0.0]    # Right wrist

        # Hips (lower torso)
        pose[11] = [-0.1, 0.3, 0.0]    # Left hip
        pose[12] = [0.1, 0.3, 0.0]     # Right hip

        # Knees (straight down)
        pose[13] = [-0.1, 0.6, 0.0]    # Left knee
        pose[14] = [0.1, 0.6, 0.0]     # Right knee

        # Ankles (feet)
        pose[15] = [-0.1, 0.9, 0.0]    # Left ankle
        pose[16] = [0.1, 0.9, 0.0]     # Right ankle

        # Other landmarks (ears, hands, feet) - fill with reasonable defaults
        # Left hand details
        pose[17] = [-0.15, 0.2, 0.0]   # Left pinky
        pose[19] = [-0.15, 0.2, 0.0]   # Left index

        # Right hand details
        pose[18] = [0.15, 0.2, 0.0]    # Right pinky
        pose[20] = [0.15, 0.2, 0.0]    # Right index

        # Left leg details
        pose[21] = [-0.1, 0.9, 0.0]    # Left big toe
        pose[23] = [-0.1, 0.9, 0.0]    # Left heel

        # Right leg details
        pose[22] = [0.1, 0.9, 0.0]     # Right big toe
        pose[24] = [0.1, 0.9, 0.0]     # Right heel

        # Remaining body parts (fill with symmetric defaults)
        for i in range(25, 33):
            pose[i] = [0.0, 0.0, 0.0]

        return pose

    @staticmethod
    def from_landmarks(landmarks, visibility=None):
        """
        Create a reference pose from detected landmarks.

        Args:
            landmarks: numpy array of shape (33, 3)
            visibility: optional visibility scores (not used for reference, but kept for compatibility)

        Returns:
            ReferencePose object
        """
        return ReferencePose(landmarks=landmarks.copy(), name="captured")

    def get_landmark(self, joint_name):
        """Get landmark by joint name."""
        if joint_name in ALIGNMENT_JOINTS:
            idx = ALIGNMENT_JOINTS[joint_name]
            return self.landmarks[idx]
        return None

    def get_angle(self, angle_name):
        """
        Get the angle for an angle joint.

        Args:
            angle_name: name of angle joint (e.g., "left_elbow")

        Returns:
            float: angle in degrees, or None if not available
        """
        if angle_name not in ANGLE_JOINTS:
            return None

        p1_idx, p2_idx, p3_idx = ANGLE_JOINTS[angle_name]

        from pose_alignment import calculate_angle
        return calculate_angle(
            self.landmarks[p1_idx],
            self.landmarks[p2_idx],
            self.landmarks[p3_idx]
        )
