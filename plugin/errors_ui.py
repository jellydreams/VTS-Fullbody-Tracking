import numpy as np
import cv2

from info import VERSION


def error_connection_vts():
    """Display error message if there is a camera issue"""
    image = np.zeros((180, 600, 3), dtype=np.uint8)
    cv2.putText(image, text="Error: Unable to connect to Software", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(255, 255, 255), thickness=1)
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



