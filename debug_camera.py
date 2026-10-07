"""Simple camera diagnostics."""

import cv2

print("\n" + "="*80)
print("CAMERA DIAGNOSTICS")
print("="*80)

print("\nTesting camera access...")

for camera_idx in range(5):
    print(f"\nTrying camera index {camera_idx}...", end=" ")
    cap = cv2.VideoCapture(camera_idx)

    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"✅ WORKS! ({w}x{h})")

            # Try to display
            print(f"  Attempting to open window...")
            try:
                cv2.imshow(f"Camera {camera_idx}", frame)
                cv2.waitKey(100)
                cv2.destroyAllWindows()
                print(f"  ✅ Window display works")
            except Exception as e:
                print(f"  ⚠️  Window display issue: {e}")

            cap.release()
            print(f"\n✅ Camera index {camera_idx} is working!")
            break
        else:
            print("❌ Can open but can't read frames")
            cap.release()
    else:
        print("❌ Cannot open")

print("\n" + "="*80)
print("To use a different camera, edit config.py and change:")
print("  CAMERA_INDEX = 0  (change 0 to 1, 2, etc.)")
print("="*80 + "\n")
