# Architecture & Design Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application Loop                     │
│                     (main.py)                                │
│  - Opens camera, processes frames, renders UI               │
└─────────────────┬──────────────────┬──────────────────────┬──┘
                  │                  │                      │
         ┌────────▼────────┐  ┌──────▼──────┐  ┌───────────▼──┐
         │ Pose Detector   │  │ Pose         │  │ Reference    │
         │ (MediaPipe)     │  │ Alignment    │  │ Pose         │
         │                 │  │              │  │              │
         │ - detect()      │  │ - normalize_ │  │ - landmarks  │
         │ - landmarks     │  │   pose()     │  │ - get_angle()│
         │ - visibility    │  │ - calculate_ │  │              │
         └─────────────────┘  │   alignment_ │  └──────────────┘
                              │   error()    │
                              │ - calculate_ │
                              │   angle()    │
                              └──────────────┘
                                    │
                              ┌─────▼──────┐
                              │ Feedback   │
                              │ Generator  │
                              │            │
                              │ - generate_│
                              │   feedback()│
                              └────────────┘
```

## Key Design Principles

### 1. Modular Architecture

Each component has a single responsibility:

- **pose_detector.py**: Wraps MediaPipe, handles pose detection
- **pose_alignment.py**: Pure math/algorithms for normalization and comparison
- **reference_pose.py**: Data management for target poses
- **feedback.py**: Generates user-facing messages
- **main.py**: Orchestrates components and renders UI

This modularity allows:
- Easy testing of individual components
- Swapping different pose detectors
- Adding new exercises without changing core logic
- Reusing alignment logic for different applications

### 2. Pose Normalization Strategy

**Problem**: Raw pixel coordinates vary based on:
- Distance from camera
- Body size/proportions
- Camera resolution
- Body orientation

**Solution**: Normalize in three steps

1. **Centering**
   ```python
   center = (left_hip + right_hip) / 2
   normalized = (landmark - center) / scale
   ```
   - Removes translation variance
   - Centers pose at body midpoint

2. **Scaling**
   ```python
   scale = distance(left_shoulder, right_shoulder)
   normalized = landmark / scale
   ```
   - Removes size variance
   - Uses shoulder distance as body scale reference

3. **2D Projection**
   - Uses only x, y coordinates (ignores z-depth)
   - Depth is unreliable for webcams
   - Focus on posture in 2D plane

**Result**: Landmarks are in normalized space where:
- Distance between shoulders ≈ 1.0 unit
- Hip center is at origin (0, 0)
- Comparable across users and camera distances

### 3. Alignment Error Calculation

**Joint Position Error**:
```
error = euclidean_distance(normalized_live, normalized_reference)
```

**Joint Angle Error**:
```
live_angle = angle(shoulder, elbow, wrist)
ref_angle = angle(shoulder, elbow, wrist)
error = |live_angle - ref_angle|
```

**Overall Score**:
```
avg_error = mean(all_joint_errors + all_angle_errors)
score = 100 * exp(-avg_error * 2)
```

- Exponential decay provides good 0-100 mapping
- Better than linear (100 - error) for user feedback
- 0% when very misaligned, 100% when perfect

### 4. Color Coding Strategy

Configurable thresholds in degrees/units:

```python
ALIGNMENT_THRESHOLDS = {
    "green": 15.0,    # ≤15 = well-aligned
    "yellow": 30.0,   # ≤30 = needs adjustment
    "red": 100.0      # >30 = misaligned
}
```

Benefits:
- Visual feedback immediately shows problem areas
- Non-linear scale: small errors = green, small deviations = yellow
- Adjustable in config without code changes

## Data Flow

### Per-Frame Processing

```
1. Capture frame from camera
   └─> OpenCV VideoCapture

2. Detect pose
   └─> PoseDetector.detect(frame)
       └─> Returns: landmarks(33,3), visibility(33,)

3. Calculate alignment
   └─> calculate_alignment_error(live, reference)
       ├─> normalize_pose(live)
       ├─> normalize_pose(reference)
       ├─> compare positions
       ├─> compare angles
       └─> generate score (0-100%)

4. Generate feedback
   └─> generate_feedback(alignment_result)
       └─> Returns: string feedback message

5. Render visualization
   ├─> Draw reference skeleton (faint)
   ├─> Draw live skeleton (color-coded)
   ├─> Draw alignment score
   ├─> Draw feedback text
   └─> Display via OpenCV imshow()

6. Display and wait for input
   └─> Check for 'q' key to quit
```

## Extending for New Exercises

### Adding a New Exercise (e.g., Squat)

**Step 1**: Create exercise-specific reference pose

```python
# In reference_pose.py

class SquatReferencePose(ReferencePose):
    def __init__(self):
        super().__init__(name="squat_bottom")
        landmarks = self._create_squat_pose()
        self.landmarks = landmarks
    
    def _create_squat_pose(self):
        pose = np.zeros((33, 3))
        # Define joints for squat position
        # Knees bent ~90 degrees, torso upright
        pose[5] = [-0.15, -0.2, 0.0]   # Left shoulder
        pose[6] = [0.15, -0.2, 0.0]    # Right shoulder
        # ... position other joints for squat
        return pose
```

**Step 2**: Create exercise-specific feedback

```python
# In feedback.py

EXERCISE_FEEDBACK = {
    "squat": {
        "left_knee": "Keep knees tracking over toes",
        "torso": "Keep chest up, don't lean forward",
        # ...
    }
}
```

**Step 3**: Create exercise selector in main

```python
# In main.py

def __init__(self):
    self.exercise = "upright"  # or "squat", "lunge", etc.
    self.reference_poses = {
        "upright": ReferencePose(),
        "squat": SquatReferencePose(),
        # ...
    }

def select_exercise(self):
    self.reference_pose = self.reference_poses[self.exercise]
```

### Key Files to Modify

1. **reference_pose.py** - Add exercise-specific pose classes
2. **feedback.py** - Add exercise-specific feedback messages
3. **config.py** - Add exercise-specific thresholds if needed
4. **main.py** - Add exercise selection UI

## Advanced Features (Future)

### Rep Counting
- Detect exercise phase transitions (up/down)
- Track repetition count
- Store set history

### Machine Learning
- Train classifier to recognize exercise type
- Personalized form validation
- Anomaly detection for form breakdowns

### Cloud Integration
- Send pose data to server for analysis
- Store user progress over time
- Compare against professional trainers

### Multi-Camera
- Use multiple camera angles
- Reconstruct 3D pose
- Better depth understanding

## Performance Optimization

### Current Performance
- Frame processing: ~33ms (30 FPS)
- CPU usage: 15-30%
- Memory: 500MB-1GB

### Optimization Strategies

1. **Reduce Resolution**
   ```python
   CAMERA_WIDTH = 640  # Instead of 1280
   CAMERA_HEIGHT = 480
   ```

2. **Skip Frames**
   ```python
   if frame_count % 2 == 0:  # Process every other frame
       alignment = calculate_alignment_error(...)
   ```

3. **Reduce Landmarks**
   - Only track relevant joints per exercise
   - Skip unused landmarks

4. **GPU Acceleration**
   - MediaPipe can use GPU
   - Enable CUDA for OpenCV if available

## Testing Strategy

### Unit Tests (Future)

```python
# Test normalization
def test_normalize_pose():
    pose1 = get_sample_pose()
    pose1_scaled = pose1 * 2  # 2x larger
    norm1 = normalize_pose(pose1)
    norm2 = normalize_pose(pose1_scaled)
    assert norm1 ≈ norm2  # Should be similar
```

### Integration Tests

```python
# Test alignment calculation
def test_alignment_perfect_match():
    ref = ReferencePose()
    result = calculate_alignment_error(ref.landmarks, ref.landmarks)
    assert result["overall_score"] > 95  # Should be nearly perfect
```

### Manual Testing

1. Stand in upright position → expect high score
2. Deliberately misalign one joint → expect red for that joint
3. Partially misalign → expect yellow
4. Verify feedback is helpful

## Known Limitations & Trade-offs

| Limitation | Reason | Future Solution |
|-----------|--------|-----------------|
| Single reference pose | Simplicity for MVP | Multiple poses per exercise |
| No rep counting | Complex state tracking | Add phase detection |
| Generic feedback | Exercise-agnostic design | Exercise-specific rules |
| 2D only | Webcam limitations | Multi-camera or depth sensor |
| Requires full body | MediaPipe needs landmarks | Partial body fallback |
| No history | Stateless design | Add database |
| CPU-only | Limits performance | GPU acceleration |

## Code Quality Standards

- **Comments**: Explain WHY, not WHAT
- **Functions**: Single responsibility, <50 lines
- **Naming**: Descriptive, no abbreviations
- **Type hints**: Added for clarity (optional, not enforced)
- **Error handling**: Graceful degradation on missing landmarks
- **Testing**: Manual verification of key functions

## Configuration Management

All hardcoded values are in `config.py`:

```python
# Thresholds
ALIGNMENT_THRESHOLDS = {...}

# Visual settings
COLORS = {...}
JOINT_RADIUS = 6

# Camera settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Algorithm parameters
CONFIDENCE_THRESHOLD = 0.5
REFERENCE_ALPHA = 0.4
```

To adjust behavior:
1. Edit `config.py` values
2. No code changes needed
3. Easy A/B testing of parameters
