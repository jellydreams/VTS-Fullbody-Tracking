import mediapipe as mp
from mediapipe.tasks import python
import numpy as np
import pyvts
import asyncio
import cv2
import os

from info import VERSION
from plugin.ui import window_tracking_configuration, NIZIMA_LIVE, VTUBE_STUDIO
from plugin.mediapipe import get_bodyparts_values, MediapipeTracking, LIVE_STREAM, IMAGE
from plugin.vtube_studio import connection_vts, create_parameters_vts, send_paramters_vts

from plugin.nizima import Nizima

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
    mt = MediapipeTracking(mode=settings['tracking_mode'])
    options = mt.init_mediapipe_options(model_path)
    PoseLandmarker = mp.tasks.vision.PoseLandmarker

    connection = False
    software = settings['software']
    port = settings['port']

    # ----- NIZIMA -------------
    if software == NIZIMA_LIVE:
        plugin_infos = {
            "Name": 'Fullbody Tracking',
            "Developer": 'Jelly Dreams'
        }
        nz = Nizima(plugin_infos=plugin_infos, port=port)
        await nz.connect_nizima()

        if nz.connection:
            connection = True
            await nz.create_parameters()

    # ----- VTUBE STUDIO -------------
    elif software == VTUBE_STUDIO:
        vts_api['port'] = port
        vts = pyvts.vts(plugin_info=plugin_info, vts_api_info=vts_api)

        error = False
        try:
            await connection_vts(vts)
        except ConnectionError:
            error_connection_vts()
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            error = True

        if not error:
            connection = True
            await create_parameters_vts(vts)

    # ---- LIVE TRACKING ----------------
    if connection:
        parameters = None
        timestamp = 0

        # -- Camera connection
        camera_setting = settings['camera_id'] if not settings['camera_url'] else settings['camera_url']
        cap = cv2.VideoCapture(camera_setting)
        if not cap.isOpened():
            error_camera_url(camera_setting)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        #print('========== START LIVE TRACKING =========')
        with PoseLandmarker.create_from_options(options) as landmarker:
            # -- LOOP Through Video
            while cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    timestamp += 1
                    # Detect pose landmarks from the current frame
                    input_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                    if mt.mode == LIVE_STREAM:
                        landmarker.detect_async(input_image, timestamp)
                        RESULT = mt.result
                    else:
                        RESULT = landmarker.detect(input_image) # IMAGE

                    # Display Image for tracking window
                    image = render_image(input_image, settings['preview_enabled'])
                    if RESULT:
                        if RESULT.pose_world_landmarks:
                            # Get coordinates
                            parameters = RESULT
                            image = mt.draw_landmarks_on_image(image, RESULT)
                        else:
                            error_pose_estimation(image)

                    # - WINDOW : CAMERA TRACKING
                    cv2.imshow(f'VTS FullBody Tracking {VERSION}', image)

                    # SEND DATA TO VTUBE STUDIO
                    if parameters:
                        data = get_bodyparts_values(parameters)

                        if software == NIZIMA_LIVE:
                            data = [{"Id": key, "Value": value*10} for key, value in data.items()]
                            await nz.set_live_parameter_values(data)
                        elif software == VTUBE_STUDIO:
                            # Prepare values to send
                            names, values = zip(*data.items())
                            await send_paramters_vts(vts, values, names)
                else:
                    if settings['camera_url']:
                        error_camera_url(camera_setting)
                    else:
                        error_camera()

                # print('-----------------------------------------')
                # Closing Plugin : Esc or Q
                if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
                    cv2.destroyAllWindows()
                    break
    else:
        print('connection error')
        error_connection_vts()
        if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
            cv2.destroyAllWindows()


def error_connection_vts():
    """Display error message if there is a camera issue"""
    image = np.zeros((180, 600, 3), dtype=np.uint8)
    cv2.putText(image, text="Error: Unable to connect to VTube Studio", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 255, 255), thickness=1)
    cv2.putText(image, text="- Ensure VTube Studio is running", org=(50, 75), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 255, 255), thickness=1)
    cv2.putText(image, text='- Enable "Start API (Allow Plugin)" in VTube Studio settings', org=(50, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 255, 255), thickness=1)
    cv2.putText(image, text="- Verify that the API Port matches in the plugin and VTube Studio", org=(50, 125), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(255, 255, 255), thickness=1)
    cv2.imshow(f'VTS FullBody Tracking {VERSION}', image)


def error_pose_estimation(image):
    """Display information when no tracking is available"""
    cv2.putText(image, text="No Human Detected", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255, 255, 255), thickness=1)


def error_camera():
    # Display error message if there is a camera issue
    image = np.zeros((100, 500, 3), dtype=np.uint8)
    cv2.putText(image, text="Problem with Camera", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 255, 255), thickness=1)
    cv2.imshow(f'VTS FullBody Tracking {VERSION}', image)


def error_camera_url(camera_setting):
    input_image = np.zeros((200, 800, 3), dtype=np.uint8)
    cv2.putText(input_image, text=f"Failed to connect to the camera at URL: {camera_setting}", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(255, 255, 255), thickness=1)
    cv2.imshow(f'VTS FullBody Tracking {VERSION}', input_image)


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

