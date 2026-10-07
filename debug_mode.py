"""Debug mode - shows what's happening frame by frame."""

import cv2
import numpy as np
from pose_detector import PoseDetector
from config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

print("\n" + "="*80)
print("POSTURE ALIGNMENT - DEBUG MODE")
print("="*80)
print("\nMonitoring camera and pose detection in real-time...")
print("Press 'q' to quit.\n")

# Initialize camera
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
    print(f"   Tried camera index: {CAMERA_INDEX}")
    print("   Solutions:")
    print("   1. Check if webcam is connected")
    print("   2. Try different camera index in config.py (0, 1, 2, etc.)")
    print("   3. Check if another app is using the camera")
    exit(1)

print("✅ Camera opened successfully")

# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"✅ Camera resolution: {int(actual_width)} x {int(actual_height)}")

# Initialize pose detector
try:
    detector = PoseDetector()
    print("✅ Pose detector initialized")
except Exception as e:
    print(f"❌ ERROR: Could not initialize pose detector: {e}")
    exit(1)

frame_count = 0
detection_count = 0

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ ERROR: Failed to read frame from camera")
            break

        frame = cv2.flip(frame, 1)  # Mirror
        h, w = frame.shape[:2]

        # Detect pose
        landmarks, visibility, _ = detector.detect(frame)

        frame_count += 1

        # Print status every 30 frames
        if frame_count % 30 == 0:
            if landmarks is not None:
                detection_count += 1
                print(f"\n✅ Frame {frame_count}: POSE DETECTED!")
                print(f"   Landmarks shape: {landmarks.shape}")
                print(f"   Visibility range: [{visibility.min():.2f}, {visibility.max():.2f}]")

                # Check visibility of key joints
                print(f"   Key joints visibility:")
                key_joints = {
                    "Nose": 0,
                    "Left shoulder": 5,
                    "Right shoulder": 6,
                    "Left hip": 11,
                    "Right hip": 12,
                    "Left knee": 13,
                    "Right knee": 14,
                    "Left ankle": 15,
                    "Right ankle": 16,
                }
                for name, idx in key_joints.items():
                    vis = visibility[idx]
                    status = "✓" if vis > 0.5 else "✗"
                    print(f"     {status} {name}: {vis:.2f}")
            else:
                print(f"\n❌ Frame {frame_count}: NO POSE DETECTED")
                print(f"   (This is expected for the first few frames)")

        # Display frame
        if landmarks is not None:
            # Draw simple skeleton
            h, w = frame.shape[:2]

            # Normalize to pixel coordinates
            scale = min(w, h) * 0.3
            for landmark in landmarks:
                x = int(w/2 + landmark[0] * scale)
                y = int(h/2 + landmark[1] * scale)
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            # Add text
            cv2.putText(frame, f"POSE DETECTED ({detection_count})",
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Searching for pose... (face camera, full body visible)",
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Frames: {frame_count}",
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

        # Show instructions
        cv2.putText(frame, "DEBUG MODE - Press 'q' to quit",
                   (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Pose Detection - Debug Mode", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

except KeyboardInterrupt:
    print("\n\nInterrupted by user")

finally:
    cap.release()
    detector.close()
    cv2.destroyAllWindows()

    print("\n" + "="*80)
    print("DEBUG SESSION SUMMARY")
    print("="*80)
    print(f"Total frames processed: {frame_count}")
    print(f"Successful detections: {detection_count}")

    if detection_count == 0:
        print("\n❌ NO POSES DETECTED")
        print("\nTroubleshooting checklist:")
        print("  1. Is your FULL BODY in frame? (head to feet)")
        print("  2. Is the LIGHTING good? (not too dark)")
        print("  3. Are you FACING the camera? (chest toward camera)")
        print("  4. Are you at right DISTANCE? (2-3 feet away)")
        print("  5. Are you wearing CONTRASTING colors?")
        print("  6. Is your WEBCAM working?")
        print("\nNext steps:")
        print("  • Try: python debug_camera.py (to verify camera)")
        print("  • Try: python -c \"import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())\"")
        print("  • If camera works, try different positioning (more light, closer to camera, etc.)")
    else:
        print(f"\n✅ Detection working! Success rate: {detection_count}/{frame_count} ({100*detection_count/frame_count:.1f}%)")

    print("="*80 + "\n")
