"""Pose detection using MediaPipe 1.0.1 Tasks API."""

import numpy as np
import cv2
import os
from config import CONFIDENCE_THRESHOLD


class PoseDetector:
    """Detects body pose using MediaPipe Pose (1.0.1 Tasks API)."""

    def __init__(self):
        """Initialize MediaPipe Pose detector with Tasks API."""
        self.pose = None
        self.api_version = None
        self.mp = None
        self.vision = None

        try:
            from mediapipe.tasks.python import vision
            from mediapipe.tasks import python
            import mediapipe as mp

            print("✓ Initializing MediaPipe 1.0.1 Tasks API...")

            # Try to find model file - check both names
            model_path = None
            for filename in ['pose_landmarker_heavy.task', 'pose_landmarker.task']:
                if os.path.exists(filename):
                    if os.path.getsize(filename) > 1000000:  # At least 1MB
                        model_path = filename
                        print(f"  ✓ Found model: {filename}")
                        break

            if model_path is None:
                raise FileNotFoundError("No pose_landmarker model file found!")

            # Initialize PoseLandmarker
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE
            )
            self.pose = vision.PoseLandmarker.create_from_options(options)
            self.api_version = "1.0+"
            self.mp = mp
            self.vision = vision
            print("✓ MediaPipe 1.0.1 initialized successfully!")

        except Exception as e:
            print(f"❌ ERROR: Could not initialize MediaPipe")
            print(f"   Problem: {e}")
            self.api_version = "none"

    def detect(self, frame):
        """
        Detect pose in a frame using MediaPipe 1.0.1.

        Args:
            frame: OpenCV frame (BGR format)

        Returns:
            tuple: (landmarks, visibility, frame_rgb)
                - landmarks: array of (x, y, z) for each of 33 joints, or None
                - visibility: array of confidence scores for each joint, or None
                - frame_rgb: RGB version of the frame
        """
        if self.pose is None or self.api_version == "none":
            return None, None, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            # Convert to MediaPipe Image
            mp_image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=frame_rgb)

            # Detect pose
            results = self.pose.detect(mp_image)

            # Check if pose was detected
            if results.pose_landmarks is None or len(results.pose_landmarks) == 0:
                return None, None, frame_rgb

            # Extract landmarks from first detected person
            landmarks = []
            visibility = []

            for landmark in results.pose_landmarks[0]:
                landmarks.append([landmark.x, landmark.y, landmark.z])
                vis = landmark.visibility if hasattr(landmark, 'visibility') else 1.0
                visibility.append(vis)

            return np.array(landmarks), np.array(visibility), frame_rgb

        except Exception as e:
            print(f"Pose detection error: {e}")
            return None, None, frame_rgb

    def close(self):
        """Release resources."""
        # Tasks API doesn't require explicit close
        pass
