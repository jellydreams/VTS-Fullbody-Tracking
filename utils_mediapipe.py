from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

from enum import Enum
import cv2


class BodyParts(Enum):
    """
    Enum class defining body parts available in Mediapipe.
    """

    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


def draw_landmarks_on_image(rgb_image, detection_result, preview=False, annotated=False):
    """
    Draw landmarks on the input image.

    :param rgb_image: input image
    :param detection_result: result of landmark detection
    :param preview: Whether to display the original image
    :param annotated: Whether to annotate landmarks with their coordinates
    :return: Image with landmarks
    """

    # Fetch the image coordinates of the pose landmarks for drawing the pose on the image
    pose_landmarks_list = detection_result.pose_landmarks

    # -- Display the original input or an empty image as a base
    if preview:
        # Use the input image as a base if preview configuration is enabled
        annotated_image = np.copy(rgb_image)
    else:
        # Create an empty image with the same dimensions as the input image
        height, width, _ = rgb_image.shape
        annotated_image = np.zeros((height, width, 3), dtype=np.uint8)

    # - Loop through the detected poses to visualize
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # -- Draw the pose landmarks
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
          landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
          annotated_image,
          pose_landmarks_proto,
          solutions.pose.POSE_CONNECTIONS,
          solutions.drawing_styles.get_default_pose_landmarks_style())

        # -- Draw annotated values on the image
        if annotated:

            i = 0
            pworld = detection_result.pose_world_landmarks[0]

            for landmark in pose_landmarks:
                # Convert normalized coordinates to image coordinates
                image_height, image_width, _ = annotated_image.shape
                landmark_px = (int(landmark.x * image_width), int(landmark.y * image_height))

                # Add x, y, z values next to each landmark
                text = f"x: {pworld[i].x:.2f}"
                cv2.putText(annotated_image, text, (landmark_px[0], landmark_px[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 212, 0), 1, cv2.LINE_AA)
                text = f"y: {pworld[i].y:.2f}"
                cv2.putText(annotated_image, text, (landmark_px[0], landmark_px[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(112, 0, 255), 1, cv2.LINE_AA)
                text = f"z: {pworld[i].z:.2f}"
                cv2.putText(annotated_image, text, (landmark_px[0], landmark_px[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 255, 90), 1, cv2.LINE_AA)

                i += 1

    return annotated_image
