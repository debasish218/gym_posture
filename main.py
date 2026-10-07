"""Main application for real-time posture alignment."""

import cv2
import numpy as np
import sys
from pose_detector import PoseDetector
from pose_alignment import calculate_alignment_error
from reference_pose import ReferencePose
from feedback import generate_feedback
from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS,
    COLORS, SKELETON_CONNECTIONS, ALIGNMENT_JOINTS, FONT, FONT_SCALE,
    FONT_THICKNESS, JOINT_RADIUS, SKELETON_THICKNESS, CONFIDENCE_THRESHOLD,
    REFERENCE_ALPHA
)


class PostureAlignmentApp:
    """Real-time posture alignment application."""

    def __init__(self):
        """Initialize the application."""
        self.cap = None
        self.pose_detector = None
        self.reference_pose = None
        self.frame_count = 0
        self.current_alignment = None

    def setup(self):
        """Initialize camera and pose detector."""
        # Initialize camera
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            print("ERROR: Could not open camera.")
            return False

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        print(f"Camera opened successfully.")
        print(f"Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))} x "
              f"{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"FPS: {self.cap.get(cv2.CAP_PROP_FPS)}")

        # Initialize pose detector
        try:
            self.pose_detector = PoseDetector()
            print("Pose detector initialized successfully.")
        except Exception as e:
            print(f"ERROR: Could not initialize pose detector: {e}")
            return False

        # Create reference pose (default upright posture)
        self.reference_pose = ReferencePose(name="upright_standing")
        print("Reference pose created (upright standing position).")

        return True

    def draw_skeleton(self, frame, landmarks, visibility=None, color=None, alpha=1.0, is_reference=False):
        """
        Draw skeleton on frame.

        Args:
            frame: OpenCV frame to draw on
            landmarks: numpy array of shape (33, 3) with normalized landmarks
            visibility: optional visibility scores
            color: tuple (B, G, R) or None for default
            alpha: transparency (0-1)
            is_reference: if True, draw with lower opacity
        """
        if landmarks is None:
            return

        # Get frame dimensions
        h, w = frame.shape[:2]

        # Convert normalized landmarks to pixel coordinates
        pixel_landmarks = self._norm_to_pixel(landmarks, w, h)

        # Draw skeleton connections
        for connection in SKELETON_CONNECTIONS:
            start_idx, end_idx = connection

            if start_idx >= len(pixel_landmarks) or end_idx >= len(pixel_landmarks):
                continue

            start = pixel_landmarks[start_idx]
            end = pixel_landmarks[end_idx]

            # Check visibility
            if visibility is not None:
                if visibility[start_idx] < CONFIDENCE_THRESHOLD or visibility[end_idx] < CONFIDENCE_THRESHOLD:
                    continue

            # Draw line
            if is_reference:
                # Reference skeleton is semi-transparent gray
                overlay = frame.copy()
                cv2.line(overlay, tuple(map(int, start)), tuple(map(int, end)),
                        COLORS["reference"], SKELETON_THICKNESS)
                frame = cv2.addWeighted(overlay, REFERENCE_ALPHA, frame, 1 - REFERENCE_ALPHA, 0)
            else:
                # Draw line with specified color
                draw_color = color if color is not None else COLORS["live"]
                cv2.line(frame, tuple(map(int, start)), tuple(map(int, end)),
                        draw_color, SKELETON_THICKNESS)

        # Draw joints
        for i, landmark in enumerate(pixel_landmarks):
            if visibility is not None and visibility[i] < CONFIDENCE_THRESHOLD:
                continue

            x, y = int(landmark[0]), int(landmark[1])

            if is_reference:
                # Reference joints are gray
                cv2.circle(frame, (x, y), JOINT_RADIUS // 2, COLORS["gray"], -1)
            else:
                # Draw joint with specified color
                draw_color = color if color is not None else COLORS["white"]
                cv2.circle(frame, (x, y), JOINT_RADIUS, draw_color, -1)

    def draw_alignment_skeleton(self, frame, landmarks, alignment_result):
        """
        Draw skeleton with color-coded alignment.

        Args:
            frame: OpenCV frame to draw on
            landmarks: numpy array of shape (33, 3)
            alignment_result: dict from calculate_alignment_error()
        """
        if landmarks is None:
            return

        h, w = frame.shape[:2]
        pixel_landmarks = self._norm_to_pixel(landmarks, w, h)

        # Get joint statuses
        joint_statuses = alignment_result["joint_statuses"]

        # Draw connections
        for connection in SKELETON_CONNECTIONS:
            start_idx, end_idx = connection

            if start_idx >= len(pixel_landmarks) or end_idx >= len(pixel_landmarks):
                continue

            start = pixel_landmarks[start_idx]
            end = pixel_landmarks[end_idx]

            # Determine color based on average status of connected joints
            start_joint_name = self._get_joint_name(start_idx)
            end_joint_name = self._get_joint_name(end_idx)

            start_status = joint_statuses.get(start_joint_name, "gray")
            end_status = joint_statuses.get(end_joint_name, "gray")

            # Use the worse status
            if start_status == "red" or end_status == "red":
                color = COLORS["red"]
            elif start_status == "yellow" or end_status == "yellow":
                color = COLORS["yellow"]
            else:
                color = COLORS["green"]

            cv2.line(frame, tuple(map(int, start)), tuple(map(int, end)), color, SKELETON_THICKNESS)

        # Draw joints with alignment colors
        for joint_name, idx in ALIGNMENT_JOINTS.items():
            if idx >= len(pixel_landmarks):
                continue

            x, y = int(pixel_landmarks[idx][0]), int(pixel_landmarks[idx][1])
            status = joint_statuses.get(joint_name, "gray")
            color = COLORS.get(status, COLORS["white"])

            cv2.circle(frame, (x, y), JOINT_RADIUS, color, -1)
            cv2.circle(frame, (x, y), JOINT_RADIUS, COLORS["white"], 1)

    def _norm_to_pixel(self, landmarks, frame_width, frame_height):
        """Convert normalized landmarks to pixel coordinates."""
        if landmarks.shape[1] == 2:
            # Already 2D normalized
            norm_2d = landmarks
        else:
            # 3D, extract x, y
            norm_2d = landmarks[:, :2]

        # Unnormalize: scale and center
        left_hip_idx = 11
        right_hip_idx = 12
        left_shoulder_idx = 5
        right_shoulder_idx = 6

        center_x = (norm_2d[left_hip_idx, 0] + norm_2d[right_hip_idx, 0]) / 2.0
        center_y = (norm_2d[left_hip_idx, 1] + norm_2d[right_hip_idx, 1]) / 2.0

        shoulder_dist = np.linalg.norm(
            norm_2d[right_shoulder_idx] - norm_2d[left_shoulder_idx]
        )
        if shoulder_dist < 0.01:
            shoulder_dist = 0.1

        # Estimate scale based on frame aspect ratio
        scale = min(frame_width, frame_height) * 0.3

        pixel_landmarks = np.zeros_like(norm_2d)
        for i in range(len(norm_2d)):
            pixel_landmarks[i, 0] = frame_width / 2.0 + norm_2d[i, 0] * scale
            pixel_landmarks[i, 1] = frame_height / 2.0 + norm_2d[i, 1] * scale

        return pixel_landmarks

    def _get_joint_name(self, landmark_idx):
        """Get joint name from landmark index."""
        for name, idx in ALIGNMENT_JOINTS.items():
            if idx == landmark_idx:
                return name
        return None

    def draw_ui(self, frame, alignment_result):
        """
        Draw UI elements (score, feedback, etc.).

        Args:
            frame: OpenCV frame to draw on
            alignment_result: dict from calculate_alignment_error()
        """
        h, w = frame.shape[:2]

        # Draw semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 180), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # Overall score
        score = alignment_result["overall_score"]
        score_text = f"Alignment: {score:.1f}%"
        cv2.putText(frame, score_text, (20, 50), FONT, FONT_SCALE + 0.3,
                   COLORS["white"], FONT_THICKNESS + 1)

        # Feedback
        feedback = generate_feedback(alignment_result)
        # Wrap feedback text
        words = feedback.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 40:
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        lines.append(" ".join(current_line))

        y_offset = 90
        for line in lines[:2]:  # Show max 2 lines
            cv2.putText(frame, line, (20, y_offset), FONT, FONT_SCALE - 0.2,
                       COLORS["white"], FONT_THICKNESS - 1)
            y_offset += 35

        # Instructions
        cv2.putText(frame, "Press 'q' to quit", (10, h - 20), FONT, 0.6,
                   COLORS["gray"], 1)

    def run(self):
        """Main application loop."""
        if not self.setup():
            return

        print("\nStarting application...")
        print("Stand in front of the camera in an upright position.")
        print("Press 'q' to quit.\n")

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    print("ERROR: Failed to read frame from camera.")
                    break

                # Detect pose on ORIGINAL frame (before flipping)
                landmarks, visibility, _ = self.pose_detector.detect(frame)

                # Flip frame for mirror effect (AFTER detection)
                frame = cv2.flip(frame, 1)

                if landmarks is not None:
                    # Calculate alignment
                    self.current_alignment = calculate_alignment_error(
                        landmarks,
                        self.reference_pose.landmarks,
                        use_angles=True
                    )

                    # Draw reference skeleton (faintly)
                    self.draw_skeleton(frame, self.reference_pose.landmarks,
                                      is_reference=True)

                    # Draw live skeleton with color coding
                    self.draw_alignment_skeleton(frame, landmarks, self.current_alignment)

                    # Draw UI
                    self.draw_ui(frame, self.current_alignment)
                else:
                    # No pose detected
                    cv2.putText(frame, "No pose detected. Adjust your position.",
                               (50, frame.shape[0] // 2), FONT, FONT_SCALE,
                               COLORS["red"], FONT_THICKNESS)

                # Display frame
                cv2.imshow("Posture Alignment", frame)

                # Handle key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting application...")
                    break

                self.frame_count += 1

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()

        if self.pose_detector is not None:
            self.pose_detector.close()

        cv2.destroyAllWindows()
        print("Resources released. Goodbye!")


def main():
    """Entry point."""
    app = PostureAlignmentApp()
    app.run()


if __name__ == "__main__":
    main()
