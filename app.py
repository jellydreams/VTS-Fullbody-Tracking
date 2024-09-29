import mediapipe as mp
from mediapipe.tasks import python
import numpy as np

import pyvts
import asyncio
import cv2
import os

from utils_mediapipe import draw_landmarks_on_image, get_parameters_names, get_bodyparts_values
from ui import window_tracking_configuration
from info import VERSION

RESULT = None

model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models/pose_landmarker_full.task'))
icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icon.png'))

plugin_info = {
    "plugin_name": "VTS_Fullbody_Tracking",
    "developer": "JellyDreams",
    "authentication_token_path": "./token.txt",
    "plugin_icon": icon_path
}

vts_api = {"version": "1.0", "name": "VTubeStudioPublicAPI", "port": 8001}


async def main(settings):
    # ----- MEDIAPIPE: LANDMARKER CONFIGURATION -----------

    vts_api['port'] = settings['port']

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
    vts = pyvts.vts(plugin_info=plugin_info, vts_api_info=vts_api)
    await vts.connect()

    # Authenticate with VTube Studio API
    #print('authentification VtubeStudio..')
    await vts.request_authenticate_token()  # get token
    await vts.request_authenticate()  # use token

    #TODO: Error Message if Vtube Studio not open
    #TODO: Error Message if Port cant connect

    # ---- VTUBE STUDIO: INITIATE CUSTOM PARAMETERS ------

    #print('Create parameters in VTube Studio')

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

        #print('========== START LIVE TRACKING =========')

        cap = cv2.VideoCapture(settings['camera_id'])

        with PoseLandmarker.create_from_options(options) as landmarker:

            # -- LOOP Through Video
            while cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    timestamp += 1

                    # Detect pose landmarks from the current frame
                    input_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                    landmarker.detect_async(input_image, timestamp)

                    # Display Image for tracking window
                    image = render_image(input_image, settings['preview_enabled'])

                    if RESULT:
                        if RESULT.pose_world_landmarks:
                            # Get coordinates
                            parameters = RESULT
                            # Display pose result
                            image = draw_landmarks_on_image(image, RESULT)
                        else:
                            # Display information when no tracking is available
                            cv2.putText(image, text="No Human Detected", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255, 255, 255) , thickness=1)

                    # - WINDOW : CAMERA TRACKING
                    cv2.imshow(f'VTS FullBody Tracking {VERSION}', image)

                    # SEND DATA TO VTUBE STUDIO
                    if parameters:
                        # Prepare values to send
                        data = get_bodyparts_values(parameters)
                        values = list(data.values())
                        names = list(data.keys())

                        # print('Update parameters in Vtube Studio')
                        # -- Update parameters in VTube Studio
                        send_request_parameter = vts.vts_request.requestSetMultiParameterValue(names, values, weight=1, face_found=True, mode='set')
                        await vts.request(send_request_parameter)
                else:
                    # Display error message if there is a camera issue
                    image = np.zeros((100, 500, 3), dtype=np.uint8)
                    cv2.putText(image, text="Problem with Camera", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 255, 255), thickness=1)
                    cv2.imshow(f'VTS FullBody Tracking {VERSION}', image)

                # Closing Plugin : Esc or Q
                if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                    cv2.destroyAllWindows()
                    running = False
                    break


def render_image(image, preview_enabled=False):
    # -- Display the original input or an empty image as a base
    image = image.numpy_view()
    if preview_enabled:
        # Use the input image as a base if preview configuration is enabled
        image = np.copy(image)
    else:
        # Create an empty image with the same dimensions as the input image
        height, width, _ = image.shape
        image = np.zeros((height, width, 3), dtype=np.uint8)

    return image


if __name__ == '__main__':

    #print('=== VTS FULLBODY TRACKING ===')

    # --- OPEN USER WINDOW : CONFIGURATION TRACKING
    root, settings = window_tracking_configuration()

    # ========= START TRACKING ==========

    asyncio.run(main(settings))

    # ========= STOP PLUGIN ==========

    root.destroy()
    #print('=== VTS FULLBODY TRACKING STOPPED ===')

