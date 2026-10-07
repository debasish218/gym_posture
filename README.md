# Real-Time AI Posture Alignment Application

A Python-based real-time posture detection and alignment system using MediaPipe Pose and OpenCV.

## Overview

This application opens your webcam and detects your body posture in real time. It compares your live posture against a reference pose and provides visual feedback with color-coded joint alignment (green/yellow/red) along with an overall alignment percentage score.

## Features

- **Real-time pose detection** using MediaPipe Pose
- **Posture normalization** to handle different body sizes and camera distances
- **Color-coded skeleton visualization**:
  - Green: correctly aligned joints
  - Yellow: partially aligned joints
  - Red: misaligned joints
- **Overall alignment score** (0-100%)
- **Real-time feedback** with correction suggestions
- **Joint angle tracking** for more robust alignment checking
- **Reference pose overlay** showing target posture
- **Modular architecture** for easy extension with new exercises

## Requirements

- Python 3.8+
- Webcam

## Installation

1. Clone or download this project.

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Download the MediaPipe pose model (~30 MB). It is not included in the repository.

```bash
wget -O pose_landmarker_heavy.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task
```

Or with curl:

```bash
curl -L -o pose_landmarker_heavy.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task
```

Place the file in the **project root**, next to `main.py`:

```
gym_postures/
├── main.py
├── pose_detector.py
├── pose_landmarker_heavy.task   <-- here
└── ...
```

The model is loaded by a path relative to the current directory, so always run the app from the project root. As an alternative, the smaller and faster `lite` or `full` models can be downloaded from the [MediaPipe Pose Landmarker page](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#models) and saved as `pose_landmarker.task`, which is used when the heavy model is missing.

4. Verify installation:

```bash
python -c "import cv2, mediapipe, numpy; print('All dependencies installed!')"
ls -lh pose_landmarker_heavy.task
```

## Usage

Run the application:

```bash
python main.py
```

**Controls:**
- **q**: Quit the application

**Instructions:**
1. Stand in front of your webcam at arm's distance.
2. Maintain an upright posture (the default reference pose).
3. Watch the skeleton visualization update in real time.
4. Joints turn green when aligned, yellow when close, red when misaligned.
5. Read the feedback text for specific correction suggestions.

## How It Works

### Pose Detection

MediaPipe Pose detects 33 body landmarks (joints) from the webcam feed at ~30 FPS.

### Pose Normalization

Raw pixel coordinates vary based on:
- Body size and proportions
- Distance from camera
- Camera resolution
- Camera angle

To handle this, landmarks are normalized by:
1. **Centering** at the midpoint between hips
2. **Scaling** by shoulder distance
3. **2D projection** (using only x, y coordinates)

### Alignment Calculation

For each important joint, the system calculates:
1. **Position error**: Euclidean distance in normalized space
2. **Angle error**: Difference in joint angles (elbow, knee, etc.)

Errors are compared against configurable thresholds:
- Error ≤ 15°/units → GREEN
- Error ≤ 30°/units → YELLOW
- Error > 30° → RED

### Overall Score

The overall alignment score (0-100%) is calculated as:
```
score = 100 * exp(-avg_error * 2)
```

where `avg_error` is the average of all joint and angle errors.

### Feedback Generation

Based on alignment results, the app generates real-time feedback:
- Identifies the 2 worst-aligned joints/angles
- Suggests specific corrections (e.g., "Raise your left shoulder")

## Project Structure

```
posture_ai/
├── main.py                  # Application entry point
├── pose_detector.py         # MediaPipe Pose integration
├── pose_alignment.py        # Normalization and alignment logic
├── reference_pose.py        # Reference pose management
├── feedback.py              # Feedback generation
├── config.py                # Configuration and constants
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Module Responsibilities

**main.py**
- Application loop and camera handling
- Frame processing and visualization
- UI rendering (score, feedback, skeleton)

**pose_detector.py**
- MediaPipe Pose initialization
- Real-time pose detection from frames

**pose_alignment.py**
- Pose normalization to handle scale/position variance
- Landmark position comparison
- Joint angle calculation and comparison
- Alignment scoring algorithm

**reference_pose.py**
- Default reference poses
- Reference pose storage and retrieval
- Support for multiple named poses

**feedback.py**
- Human-readable feedback generation
- Correction suggestions based on worst alignments

**config.py**
- Alignment thresholds (green/yellow/red)
- Display colors and styling
- Skeleton joint connections
- Camera settings

## Configuration

Edit `config.py` to customize:

### Alignment Thresholds

```python
ALIGNMENT_THRESHOLDS = {
    "green": 15.0,      # Threshold for green (well-aligned)
    "yellow": 30.0,     # Threshold for yellow (needs adjustment)
    "red": 100.0        # Threshold for red (misaligned)
}
```

### Colors

```python
COLORS = {
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "red": (0, 0, 255),
    # ... etc
}
```

### Camera Settings

```python
CAMERA_INDEX = 0              # Webcam index (0 = default)
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30
```

## Current Limitations

1. **Single reference pose**: Only supports comparison against one hardcoded upright posture.
2. **No exercise-specific logic**: Not tailored for squats, lunges, deadlifts, etc.
3. **Basic feedback**: Feedback is generic and not exercise-specific.
4. **No rep counting**: Cannot track exercise repetitions.
5. **No audio feedback**: Visual feedback only.
6. **Limited angle tracking**: Only tracks elbow and knee angles; could expand to more joints.
7. **No performance history**: Does not track user progress over time.
8. **Requires full body visibility**: Works best when the entire body is in frame.

## Future Enhancements

### Phase 1: Multiple Exercises

- Add squat-specific reference poses
- Add lunge-specific reference poses
- Create exercise selection menu
- Implement exercise-specific feedback

### Phase 2: Rep Counting

- Detect exercise phases (up/down for squat)
- Count repetitions automatically
- Display rep count and set tracker

### Phase 3: Advanced Feedback

- Voice synthesis for audio feedback
- More detailed form corrections
- Exercise progression suggestions

### Phase 4: Analytics & History

- Store per-user performance metrics
- Track improvement over time
- Generate form analysis reports
- Visualize common mistakes

### Phase 5: Mobile Integration

- REST API for client-server architecture
- Mobile app for real-time feedback
- Cloud-based form analysis

### Phase 6: Multi-Camera Support

- Combine multiple camera angles
- Better depth and 3D pose understanding
- Enhanced form detection

### Phase 7: Machine Learning Enhancement

- Train custom models for specific exercises
- Personalized form validation
- Anomaly detection for form breakdowns

## Troubleshooting

**Camera not opening:**
- Verify webcam is connected and working
- Check if another application is using the camera
- Try changing `CAMERA_INDEX` in `config.py` (e.g., 0, 1, 2)

**`No pose_landmarker model file found!`:**
- Download the model as described in step 3 of [Installation](#installation)
- Make sure the file is in the project root and you are running `python main.py` from that folder
- Check that the file is about 30 MB; an empty or partial download (under 1 MB) is ignored

**Pose not detected:**
- Ensure sufficient lighting
- Move into frame completely
- Stand at arm's distance from camera
- Verify MediaPipe is installed correctly

**Poor alignment accuracy:**
- Check if reference pose matches your current position
- Increase lighting in the room
- Ensure you're standing directly facing the camera
- Adjust thresholds in `config.py` if too strict/lenient

**Slow performance:**
- Reduce `CAMERA_WIDTH` and `CAMERA_HEIGHT` in `config.py`
- Close other applications
- Reduce overlay quality if needed

## Performance

- Typical processing time: ~33ms per frame (30 FPS)
- CPU usage: 15-30% (varies by system)
- Memory usage: ~500MB-1GB
- Best on systems with integrated GPU (auto-accelerated via MediaPipe)

## Hardware Recommendations

- CPU: Intel i5 / AMD Ryzen 5 or better
- RAM: 4GB minimum, 8GB recommended
- Webcam: 1080p recommended for best detection
- Lighting: Well-lit environment (natural light or office lighting)

## License

This project is provided as-is for educational and personal use.

## Contributing

To extend this project:

1. Add new reference poses in `reference_pose.py`
2. Implement exercise-specific logic in new modules
3. Add configuration options to `config.py`
4. Update `feedback.py` for exercise-specific messages

Example: Adding a squat exercise

```python
# In reference_pose.py
class SquatReferencePose(ReferencePose):
    def __init__(self):
        super().__init__(name="squat")
        # Define squat posture landmarks...
```

## Contact & Support

For issues or questions, review the code comments and docstrings. The modular design makes it easy to debug individual components independently.
