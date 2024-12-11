from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from enum import Enum

LIVE_STREAM = 'LIVE_STREAM'
IMAGE = 'IMAGE'

class BodyParts(Enum):
    """
    Enum class defining body parts available in Mediapipe.
    """

    #NOSE = 0
    # LEFT_EYE_INNER = 1
    # LEFT_EYE = 2
    # LEFT_EYE_OUTER = 3
    # RIGHT_EYE_INNER = 4
    # RIGHT_EYE = 5
    # RIGHT_EYE_OUTER = 6
    # LEFT_EAR = 7
    # RIGHT_EAR = 8
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

    #NOSE = BodyParts.RIGHT_HIP
    # LEFT_EYE_INNER = BodyParts.LEFT_EYE
    # LEFT_EYE = BodyParts.RIGHT_HIP
    # LEFT_EYE_OUTER = BodyParts.RIGHT_HIP
    # RIGHT_EYE_INNER = BodyParts.RIGHT_HIP
    # RIGHT_EYE = BodyParts.RIGHT_HIP
    # RIGHT_EYE_OUTER = BodyParts.RIGHT_HIP
    # LEFT_EAR = BodyParts.RIGHT_HIP
    # RIGHT_EAR = BodyParts.RIGHT_HIP
    # MOUTH_LEFT = BodyParts.RIGHT_HIP
    # MOUTH_RIGHT = BodyParts.RIGHT_HIP

    LEFT_SHOULDER = BodyParts.RIGHT_SHOULDER
    RIGHT_SHOULDER = BodyParts.LEFT_SHOULDER
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

def get_parameters_names():
    bodyparts_names = [part.name for part in BodyParts]
    # Remove unused parameter names
    bodyparts_names.remove('RIGHT_HIP')
    bodyparts_names.remove('LEFT_HIP')
    # Add custom names to the list
    # Note: If a parameter is not created and data is sent, all values will be set to 0
    bodyparts_names.extend(['HIPS_POSITION', 'BODY', 'HIPS_ROTATION', 'CLAVICLES'])
    parameters_names = [part + '_' + angle for part in bodyparts_names for angle in ['X', 'Y', 'Z', 'VISIBILITY']]

    return parameters_names


def get_bodyparts_values(parameters):
    """
    Prepare list of input parameter that will be sent to Vtube Studio
    :param parameters: landmarks mediapipe
    """
    i = 0
    values = {}

    # Get coordinates from hip as midpoint
    parameters_world = parameters.pose_world_landmarks.landmark#[0]

    # Go through each tracked body part
    for bodypart in BodyParts:
        # Find center for this part of the body
        bodypart_center_name = BodyCenters[bodypart.name]

        # Skip hips as orignal values are used
        if bodypart.name not in ['RIGHT_HIP', 'LEFT_HIP']:
            bodypart_center = parameters_world[bodypart_center_name.value.value]
            bodypart_values = parameters_world[bodypart.value]
            bodypart_name = bodypart.name

            # Calculate values from new center
            data = calcul_data(bodypart_values, bodypart_center, bodypart_name)
            values.update(data)
            i += 1

    # Retrieve coordinates from the image
    parameters_img = parameters.pose_landmarks.landmark

    values = calcul_body_position(values, parameters_img)
    values = calcul_hips_position(values, parameters_img)
    values = calcul_clavicles_position(values, parameters_world)
    values = calcul_hips_rotation(values, parameters_world)

    return values


def calcul_data(part, center, name):
    """
    Calculate body part values
    :param part: Landmarks, body part to recalculate
    :param center: Landmarks, body part used as new center
    :param name: String, name of body part to calculate
    :return: Dict with new values for each axis
    """

    x_name = name + '_X'
    y_name = name + '_Y'
    z_name = name + '_Z'
    v_name = name + '_VISIBILITY'

    x = (part.x - center.x) * 10
    y = (part.y - center.y) * 10
    z = (part.z - center.z) * 10

    data = {
        x_name: x,
        y_name: y,
        z_name: z,
        v_name: part.visibility,
        }

    return data


def calcul_body_position(values, parameters_img):
    # Use the middle of hips to control the position of the body in space using image coordinates
    values['BODY_X'] = (parameters_img[BodyParts.RIGHT_HIP.value].x + parameters_img[BodyParts.LEFT_HIP.value].x) / 2
    values['BODY_Y'] = (parameters_img[BodyParts.RIGHT_HIP.value].y + parameters_img[BodyParts.LEFT_HIP.value].y) / 2
    values['BODY_Z'] = (parameters_img[BodyParts.RIGHT_HIP.value].z + parameters_img[BodyParts.LEFT_HIP.value].z) / 2

    values['BODY_VISIBILITY'] = 1.0
    return values


def calcul_hips_position(values, parameters_img):
    # Use the right hip to control the position of the hips using body position as center
    body_center_x = (parameters_img[BodyParts.RIGHT_HIP.value].x + parameters_img[BodyParts.LEFT_HIP.value].x + parameters_img[BodyParts.RIGHT_SHOULDER.value].x + parameters_img[BodyParts.LEFT_SHOULDER.value].x + parameters_img[BodyParts.RIGHT_KNEE.value].x + parameters_img[BodyParts.LEFT_KNEE.value].x) / 6
    body_center_y = (parameters_img[BodyParts.RIGHT_HIP.value].y + parameters_img[BodyParts.LEFT_HIP.value].y + parameters_img[BodyParts.RIGHT_SHOULDER.value].y + parameters_img[BodyParts.LEFT_SHOULDER.value].y + parameters_img[BodyParts.RIGHT_KNEE.value].y + parameters_img[BodyParts.LEFT_KNEE.value].y) / 6
    body_center_z = (parameters_img[BodyParts.RIGHT_HIP.value].z + parameters_img[BodyParts.LEFT_HIP.value].z + parameters_img[BodyParts.RIGHT_SHOULDER.value].z + parameters_img[BodyParts.LEFT_SHOULDER.value].z + parameters_img[BodyParts.RIGHT_KNEE.value].z + parameters_img[BodyParts.LEFT_KNEE.value].z) / 6

    # middle_hip - center_body
    values['HIPS_POSITION_X'] = (values['BODY_X'] - body_center_x) * 100
    values['HIPS_POSITION_Y'] = (values['BODY_Y'] - body_center_y) * 10
    values['HIPS_POSITION_Z'] = (values['BODY_Z'] - body_center_z) * 10

    values['HIPS_POSITION_VISIBILITY'] = 1.0
    return values


def calcul_hips_rotation(values, parameters_world):
    values['HIPS_ROTATION_X'] = parameters_world[BodyParts.LEFT_HIP.value].x * 100
    values['HIPS_ROTATION_Y'] = parameters_world[BodyParts.LEFT_HIP.value].y * 100
    values['HIPS_ROTATION_Z'] = parameters_world[BodyParts.LEFT_HIP.value].z * 100
    return values


def calcul_clavicles_position(values, parameters_world):
    # Determine clavicle position using the hip at the center
    values['CLAVICLES_X'] = parameters_world[BodyParts.RIGHT_SHOULDER.value].x * 10
    values['CLAVICLES_Y'] = parameters_world[BodyParts.RIGHT_SHOULDER.value].y * 10
    values['CLAVICLES_Z'] = parameters_world[BodyParts.RIGHT_SHOULDER.value].z * 10
    values['CLAVICLES_VISIBILITY'] = parameters_world[BodyParts.RIGHT_SHOULDER.value].visibility
    return values
