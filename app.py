import mediapipe as mp
from mediapipe.tasks import python

import pyvts
import asyncio
import cv2
import os

from utils_mediapipe import draw_landmarks_on_image, BodyParts, BodyCenters, get_part_from_name
from ui import window_tracking_configuration

RESULT = None

model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models/pose_landmarker_full.task'))

plugin_info = {
    "plugin_name": "VTS_Fullbody_Tracking",
    "developer": "JellyDreams",
    "authentication_token_path": "./token.txt"
}


async def main(camera_id, preview_enabled):
    # ----- MEDIAPIPE: LANDMARKER CONFIGURATION -----------

    # Create a PoseLandmarker object
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult

    def set_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        global RESULT
        RESULT = result

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=set_result)

    # ----- VTUBE STUDIO: CONNECTION -------------

    # Initialize VTube Studio connection
    vts = pyvts.vts(plugin_info=plugin_info)
    await vts.connect()

    # Authenticate with VTube Studio API
    print('authentification VtubeStudio..')
    await vts.request_authenticate_token()  # get token
    await vts.request_authenticate()  # use token

    #TODO: Error Message if Vtube Studio not open

    # ---- VTUBE STUDIO: INITIATE CUSTOM PARAMETERS ------

    print('Create parameters in VTube Studio')

    # Prepare parameter names for each body part
    parameter_names = get_parameters_names()

    # Maximum of 100 parameters allowed to be created in VTube Studio per plugin
    for parameter_name in parameter_names:
        # Add custom parameters in VTube Studio
        send_request_new_parameter = vts.vts_request.requestCustomParameter(parameter_name, min=-10, max=10)
        await vts.request(send_request_new_parameter)

    # ---- LIVE TRACKING ----------------

    parameters = None
    timestamp = 0
    running = True

    while running:

        print('========== START LIVE TRACKING =========')

        cap = cv2.VideoCapture(camera_id)
        with PoseLandmarker.create_from_options(options) as landmarker:

            # -- LOOP Through Video
            while cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    timestamp += 1

                    # Detect pose landmarks from the current frame
                    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                    landmarker.detect_async(image, timestamp)

                    if RESULT:
                        if RESULT.pose_world_landmarks:
                            # Get coordinates in meters from hip as midpoint
                            parameters = RESULT.pose_world_landmarks[0]

                            # Display pose result in additional window
                            annotated_image = draw_landmarks_on_image(image.numpy_view(), RESULT, preview_enabled)
                            cv2.imshow('Body Tracking', annotated_image)
                            if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                                cv2.destroyAllWindows()
                                running = False
                                break

                    if parameters:
                        # Prepare values to send
                        data = get_bodyparts_values(parameters)
                        values = list(data.values())
                        names = list(data.keys())

                        print('Update parameters in Vtube Studio')
                        # -- Update parameters in VTube Studio
                        send_request_parameter = vts.vts_request.requestSetMultiParameterValue(names, values, weight=1, face_found=True, mode='set')
                        await vts.request(send_request_parameter)


def get_parameters_names():
    parameters_names = [body_part.name + '_' + angle for body_part in BodyParts for angle in ['X', 'Y', 'Z', 'VISIBILITY']]
    return parameters_names


def get_bodyparts_values(parameters):
    i = 0
    values = {}
    # Go through each tracked body part
    for bodypart in BodyParts:
        # Find center for this part of the body
        bodypart_center_name = BodyCenters[bodypart.name]
        bodypart_center = parameters[bodypart_center_name.value.value]
        bodypart_values = parameters[bodypart.value]
        # Calculate values from new center
        data = calcul_data(bodypart_values, bodypart_center, bodypart.name)
        values.update(data)
        i += 1
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


if __name__ == '__main__':

    print('=== VTS FULLBODY TRACKING ===')

    # --- OPEN USER WINDOW : CONFIGURATION TRACKING

    root, settings = window_tracking_configuration()
    camera_id, preview_enabled = settings
    # ========= START TRACKING ==========

    asyncio.run(main(camera_id, preview_enabled))

    # ========= STOP PLUGIN ==========

    root.destroy()
    print('=== VTS FULLBODY TRACKING STOPPED ===')

