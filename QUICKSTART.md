# Quick Start Guide

## Installation

1. Navigate to the project directory:
```bash
cd /home/zadmin/Documents/gym_postures
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
source venv/bin/activate
python main.py
```

## What You'll See

1. **Live Camera Feed**: Your webcam with skeleton overlay
2. **Reference Skeleton**: Light gray skeleton showing the target upright posture
3. **Colored Joints**: 
   - 🟢 Green: Well-aligned joints
   - 🟡 Yellow: Needs minor adjustment
   - 🔴 Red: Significantly misaligned

4. **Alignment Score**: Top-left corner shows 0-100% alignment percentage
5. **Feedback Text**: Real-time suggestions for posture corrections
6. **Instructions**: "Press 'q' to quit" at the bottom

## How to Use

1. **Position yourself**: Stand 2-3 feet away from your camera
2. **Face the camera**: Position yourself directly facing the camera
3. **Good lighting**: Ensure adequate lighting
4. **Watch the feedback**: Adjust your posture based on the color coding and text suggestions

## Example Output

```
Alignment: 87%
Excellent posture!
Raise your left shoulder. Straighten your back.
```

## Stopping the Application

Press **q** on your keyboard to quit.

## Troubleshooting

**Camera won't open:**
- Check webcam is plugged in
- Verify no other app is using it
- Try changing `CAMERA_INDEX = 0` to `1` or `2` in `config.py`

**No body detected:**
- Move further from camera (3+ feet)
- Ensure full body is in frame
- Improve lighting

**Alignment always red:**
- Check if you're standing upright
- Adjust `ALIGNMENT_THRESHOLDS` in `config.py` (make values larger)

## Next Steps

- Try different standing postures
- Examine how joints change colors
- Read the feedback and adjust accordingly
- Modify `config.py` thresholds to fine-tune sensitivity

## Architecture Overview

The app uses these key components:

1. **pose_detector.py** - MediaPipe Pose for body detection
2. **pose_alignment.py** - Normalizes poses and compares them
3. **reference_pose.py** - Stores the target posture
4. **feedback.py** - Generates helpful messages
5. **main.py** - Application loop and visualization
6. **config.py** - Thresholds and settings
