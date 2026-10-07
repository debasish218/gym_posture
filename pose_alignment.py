"""Pose alignment and normalization logic."""

import numpy as np
from config import ALIGNMENT_JOINTS, ANGLE_JOINTS, ALIGNMENT_THRESHOLDS


def calculate_angle(point_a, point_b, point_c):
    """
    Calculate angle between three points.

    The angle is at point_b, formed by vectors (a->b) and (c->b).

    Args:
        point_a: first point (x, y, z)
        point_b: vertex point (x, y, z)
        point_c: third point (x, y, z)

    Returns:
        float: angle in degrees (0-180)
    """
    a = np.array(point_a)
    b = np.array(point_b)
    c = np.array(point_c)

    # Vectors from b to a and b to c
    ba = a - b
    bc = c - b

    # Calculate angle using dot product
    # Only use x, y coordinates (ignore z depth)
    ba_2d = ba[:2]
    bc_2d = bc[:2]

    # Magnitudes
    mag_ba = np.linalg.norm(ba_2d)
    mag_bc = np.linalg.norm(bc_2d)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    # Cosine of angle
    cos_angle = np.dot(ba_2d, bc_2d) / (mag_ba * mag_bc)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    # Angle in radians, then convert to degrees
    angle_rad = np.arccos(cos_angle)
    angle_deg = np.degrees(angle_rad)

    return angle_deg


def normalize_pose(landmarks, visibility=None):
    """
    Normalize pose landmarks to be invariant to scale and position.

    Normalization steps:
    1. Center the pose at the midpoint between hips
    2. Scale by the distance between shoulders
    3. Flatten to 2D (ignore z-depth)

    Args:
        landmarks: numpy array of shape (33, 3) with raw landmarks
        visibility: optional array of visibility scores

    Returns:
        numpy array of shape (33, 2) with normalized landmarks
    """
    if landmarks is None:
        return None

    landmarks = landmarks.astype(np.float32)

    # Get hip positions (joint indices 11 and 12)
    left_hip = landmarks[11, :2]
    right_hip = landmarks[12, :2]

    # Center point (midpoint between hips)
    center = (left_hip + right_hip) / 2.0

    # Get shoulder positions (joint indices 5 and 6)
    left_shoulder = landmarks[5, :2]
    right_shoulder = landmarks[6, :2]

    # Scale factor (distance between shoulders)
    shoulder_distance = np.linalg.norm(right_shoulder - left_shoulder)
    if shoulder_distance < 0.01:
        shoulder_distance = 0.1  # Avoid division by zero

    # Normalize: center and scale
    normalized = np.zeros((landmarks.shape[0], 2), dtype=np.float32)
    for i in range(landmarks.shape[0]):
        # Use only x, y coordinates
        normalized[i] = (landmarks[i, :2] - center) / shoulder_distance

    return normalized


def calculate_alignment_error(live_landmarks, reference_landmarks, use_angles=True):
    """
    Calculate alignment error between live pose and reference pose.

    Compares both position and joint angles.

    Args:
        live_landmarks: numpy array of shape (33, 3) or (33, 2)
        reference_landmarks: numpy array of shape (33, 3) or (33, 2)
        use_angles: if True, also compare joint angles

    Returns:
        dict: {
            "overall_score": 0-100,
            "joint_errors": {
                "joint_name": error_value,
                ...
            },
            "joint_statuses": {
                "joint_name": "green" | "yellow" | "red",
                ...
            },
            "angle_errors": {
                "angle_name": error_value,
                ...
            },
            "angle_statuses": {
                "angle_name": "green" | "yellow" | "red",
                ...
            }
        }
    """
    # Normalize both poses
    live_norm = normalize_pose(live_landmarks)
    ref_norm = normalize_pose(reference_landmarks)

    if live_norm is None or ref_norm is None:
        return {
            "overall_score": 0,
            "joint_errors": {},
            "joint_statuses": {},
            "angle_errors": {},
            "angle_statuses": {}
        }

    # Calculate positional errors for each joint
    joint_errors = {}
    joint_statuses = {}

    for joint_name, idx in ALIGNMENT_JOINTS.items():
        if idx < len(live_norm) and idx < len(ref_norm):
            # Euclidean distance in normalized space
            error = np.linalg.norm(live_norm[idx] - ref_norm[idx])
            joint_errors[joint_name] = error
            joint_statuses[joint_name] = get_status(error, ALIGNMENT_THRESHOLDS)

    # Calculate angle errors if requested
    angle_errors = {}
    angle_statuses = {}

    if use_angles:
        for angle_name in ANGLE_JOINTS.keys():
            p1_idx, p2_idx, p3_idx = ANGLE_JOINTS[angle_name]

            live_angle = calculate_angle(
                live_landmarks[p1_idx],
                live_landmarks[p2_idx],
                live_landmarks[p3_idx]
            )
            ref_angle = calculate_angle(
                reference_landmarks[p1_idx],
                reference_landmarks[p2_idx],
                reference_landmarks[p3_idx]
            )

            # Angle error in degrees
            error = abs(live_angle - ref_angle)
            angle_errors[angle_name] = error
            angle_statuses[angle_name] = get_status(error, ALIGNMENT_THRESHOLDS)

    # Calculate overall alignment score
    all_errors = list(joint_errors.values()) + list(angle_errors.values())

    if len(all_errors) == 0:
        overall_score = 0
    else:
        # Average error, mapped to 0-100 score
        avg_error = np.mean(all_errors)
        # Using a simple formula: score = 100 * exp(-avg_error)
        overall_score = max(0, min(100, 100 * np.exp(-avg_error * 2)))

    return {
        "overall_score": overall_score,
        "joint_errors": joint_errors,
        "joint_statuses": joint_statuses,
        "angle_errors": angle_errors,
        "angle_statuses": angle_statuses
    }


def get_status(error_value, thresholds):
    """
    Determine status (green/yellow/red) based on error value.

    Args:
        error_value: numeric error value
        thresholds: dict with "green" and "yellow" keys

    Returns:
        str: "green", "yellow", or "red"
    """
    if error_value <= thresholds["green"]:
        return "green"
    elif error_value <= thresholds["yellow"]:
        return "yellow"
    else:
        return "red"
