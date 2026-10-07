"""Simplest possible test - just show camera feed."""

import cv2

print("\n" + "="*80)
print("SIMPLE CAMERA TEST")
print("="*80)
print("\nShowing raw camera feed (no pose detection)...")
print("This will help verify your camera works.\n")
print("Instructions:")
print("  1. Stand in front of camera")
print("  2. You should see yourself on screen")
print("  3. Move around - you should see yourself move")
print("  4. Press 'q' to quit\n")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera at index 0")
    print("\nTrying other indexes...")
    for idx in range(1, 5):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            print(f"✅ Found camera at index {idx}")
            break
    else:
        print("❌ No camera found!")
        exit(1)

print("✅ Camera opened!")

frame_count = 0
while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Cannot read from camera")
        break

    frame = cv2.flip(frame, 1)  # Mirror
    frame_count += 1

    h, w = frame.shape[:2]

    # Add info text
    cv2.putText(frame, f"Camera Feed (Frame {frame_count})",
               (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Resolution: {w}x{h}",
               (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "Press 'q' to quit",
               (20, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Simple Camera Test", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Test complete! {frame_count} frames captured")
print("If you saw yourself on screen, your camera works!")
print("="*80 + "\n")
