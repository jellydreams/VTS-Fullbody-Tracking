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
    # LEFT_EYE_INNER = 1
    # LEFT_EYE = 2
    # LEFT_EYE_OUTER = 3
    # RIGHT_EYE_INNER = 4
    # RIGHT_EYE = 5
    # RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    # MOUTH_LEFT = 9
    # MOUTH_RIGHT = 10
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


class BodyCenters(Enum):
    """
    Enum class defining the center of body parts.
    """

    NOSE = BodyParts.RIGHT_HIP
    # LEFT_EYE_INNER = BodyParts.LEFT_EYE
    # LEFT_EYE = BodyParts.RIGHT_HIP
    # LEFT_EYE_OUTER = BodyParts.RIGHT_HIP
    # RIGHT_EYE_INNER = BodyParts.RIGHT_HIP
    # RIGHT_EYE = BodyParts.RIGHT_HIP
    # RIGHT_EYE_OUTER = BodyParts.RIGHT_HIP
    LEFT_EAR = BodyParts.RIGHT_HIP
    RIGHT_EAR = BodyParts.RIGHT_HIP
    # MOUTH_LEFT = BodyParts.RIGHT_HIP
    # MOUTH_RIGHT = BodyParts.RIGHT_HIP

    LEFT_SHOULDER = BodyParts.LEFT_HIP
    RIGHT_SHOULDER = BodyParts.RIGHT_HIP
    LEFT_ELBOW = BodyParts.LEFT_SHOULDER
    RIGHT_ELBOW = BodyParts.RIGHT_SHOULDER
    LEFT_WRIST = BodyParts.LEFT_ELBOW
    RIGHT_WRIST = BodyParts.RIGHT_ELBOW
    LEFT_PINKY = BodyParts.LEFT_WRIST
    RIGHT_PINKY = BodyParts.RIGHT_WRIST
    LEFT_INDEX = BodyParts.LEFT_WRIST
    RIGHT_INDEX = BodyParts.RIGHT_WRIST
    LEFT_THUMB = BodyParts.LEFT_WRIST
    RIGHT_THUMB = BodyParts.RIGHT_WRIST

    LEFT_HIP = BodyParts.RIGHT_HIP
    RIGHT_HIP = BodyParts.LEFT_HIP
    LEFT_KNEE = BodyParts.LEFT_HIP
    RIGHT_KNEE = BodyParts.RIGHT_HIP
    LEFT_ANKLE = BodyParts.LEFT_KNEE
    RIGHT_ANKLE = BodyParts.RIGHT_KNEE
    LEFT_HEEL = BodyParts.LEFT_ANKLE
    RIGHT_HEEL = BodyParts.RIGHT_ANKLE
    LEFT_FOOT_INDEX = BodyParts.LEFT_HEEL
    RIGHT_FOOT_INDEX = BodyParts.RIGHT_HEEL


def get_part_from_name(i):
    for part in BodyParts:
        if part.value == i:
            return part
    raise None


def draw_landmarks_on_image(img, detection_result):
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

    # - Loop through the detected poses to visualize
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]

        # -- Draw the pose landmarks
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
          landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
          img,
          pose_landmarks_proto,
          solutions.pose.POSE_CONNECTIONS,
          solutions.drawing_styles.get_default_pose_landmarks_style())

    return img
