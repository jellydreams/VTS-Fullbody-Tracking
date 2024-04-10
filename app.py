import mediapipe as mp
from mediapipe.tasks import python

import pyvts
import asyncio
import cv2
import os

from utils_mediapipe import draw_landmarks_on_image, BodyParts
from ui import window_tracking_configuration

RESULT = None


model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models/pose_landmarker_full.task'))

plugin_info = {
    "plugin_name": "VTS_Fullbody_Tracking",
    "developer": "JellyDreams",
    "authentication_token_path": "./token.txt"
}


async def main(camera_id, preview_enabled, annotate_enabled):
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
    parameter_names = [body_part.name + '_' + angle for angle in ['X', 'Y', 'Z', 'VISIBILITY'] for body_part in BodyParts]

    for parameter_name in parameter_names:
        # Add custom parameters in VTube Studio
        send_request_new_parameter = vts.vts_request.requestCustomParameter(parameter_name, min=-1, max=1)
        await vts.request(send_request_new_parameter)

    # ---- LIVE TRACKING ----------------

    parameters = None
    timestamp = 0

    while True:

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
                            annotated_image = draw_landmarks_on_image(image.numpy_view(), RESULT, preview_enabled, annotate_enabled)
                            cv2.imshow('Body Tracking', annotated_image)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

                    if parameters:
                        print('Update parameters in Vtube Studio')
                        # -- Update parameters in VTube Studio
                        values = [parameters[body_part.value].__getattribute__(angle) for angle in ['x', 'y', 'z', 'visibility'] for body_part in BodyParts]
                        send_request_parameter = vts.vts_request.requestSetMultiParameterValue(parameter_names, values, weight=1, face_found=True, mode='set')
                        await vts.request(send_request_parameter)


if __name__ == '__main__':

    print('=== VTS FULLBODY TRACKING ===')

    # --- OPEN USER WINDOW : CONFIGURATION TRACKING

    camera_id, preview_enabled, annotate_enabled = window_tracking_configuration()

    # ========= START TRACKING ==========

    asyncio.run(main(camera_id, preview_enabled, annotate_enabled))

