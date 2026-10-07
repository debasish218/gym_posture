"""Feedback generation based on pose alignment."""


def generate_feedback(alignment_result, reference_pose_name="upright"):
    """
    Generate human-readable feedback based on alignment results.

    Args:
        alignment_result: dict returned from calculate_alignment_error()
        reference_pose_name: name of the reference pose

    Returns:
        str: feedback message
    """
    overall_score = alignment_result["overall_score"]
    joint_statuses = alignment_result["joint_statuses"]
    angle_statuses = alignment_result["angle_statuses"]

    # Determine overall feedback message
    if overall_score >= 80:
        feedback = "Excellent posture!"
    elif overall_score >= 60:
        feedback = "Good posture, minor adjustments needed."
    elif overall_score >= 40:
        feedback = "Posture needs improvement."
    else:
        feedback = "Significant posture correction needed."

    # Find joints and angles with the worst alignment
    worst_joints = _find_worst_alignments(joint_statuses, top_n=2)
    worst_angles = _find_worst_alignments(angle_statuses, top_n=2)

    # Add specific feedback
    corrections = []

    for joint_name, status in worst_joints:
        corrections.append(_get_joint_correction(joint_name))

    for angle_name, status in worst_angles:
        corrections.append(_get_angle_correction(angle_name))

    if corrections:
        feedback += " " + " ".join(corrections[:2])  # Limit to 2 corrections

    return feedback


def _find_worst_alignments(status_dict, top_n=3):
    """
    Find the worst alignments (most reds, then yellows).

    Args:
        status_dict: dict of joint/angle names to status ("green"/"yellow"/"red")
        top_n: number of worst items to return

    Returns:
        list of tuples (name, status)
    """
    # Prioritize red, then yellow
    priority = {"red": 2, "yellow": 1, "green": 0}

    sorted_items = sorted(
        status_dict.items(),
        key=lambda x: priority.get(x[1], 0),
        reverse=True
    )

    return sorted_items[:top_n]


def _get_joint_correction(joint_name):
    """Get correction message for a misaligned joint."""
    corrections = {
        "left_shoulder": "Raise your left shoulder.",
        "right_shoulder": "Raise your right shoulder.",
        "left_elbow": "Adjust your left elbow position.",
        "right_elbow": "Adjust your right elbow position.",
        "left_hip": "Adjust your left hip alignment.",
        "right_hip": "Adjust your right hip alignment.",
        "left_knee": "Align your left knee properly.",
        "right_knee": "Align your right knee properly.",
        "left_ankle": "Adjust your left ankle position.",
        "right_ankle": "Adjust your right ankle position.",
    }
    return corrections.get(joint_name, f"Adjust your {joint_name}.")


def _get_angle_correction(angle_name):
    """Get correction message for a misaligned angle."""
    corrections = {
        "left_elbow": "Adjust your left elbow angle.",
        "right_elbow": "Adjust your right elbow angle.",
        "left_knee": "Straighten or bend your left knee.",
        "right_knee": "Straighten or bend your right knee.",
    }
    return corrections.get(angle_name, f"Adjust your {angle_name} angle.")
