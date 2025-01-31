import mediapipe as mp
import cv2
from plugin.mediapipe import LIVE_STREAM
from plugin.errors_ui import error_camera_url, error_pose_estimation, error_camera
import numpy as np


class PoseDetection:

    def __init__(self, settings):
        self.mode = settings['tracking_mode']
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        self.settings = settings
        self.cap = None
        self.results = []
        self.parameters = []
        self.camera_setting = self.settings['camera_id'] if not self.settings['camera_url'] else self.settings['camera_url']

    def camera_connection(self):
        # -- Camera to retrieve input for pose detection
        self.camera_setting = self.settings['camera_id'] if not self.settings['camera_url'] else self.settings['camera_url']
        self.cap = cv2.VideoCapture(self.camera_setting)
        if not self.cap.isOpened():
            error_camera_url(self.camera_setting)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def detect(self, pose):
        # -- LOOP Through Video
        success, frame = self.cap.read()

        if success:
            # current frame
            input_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Flip the image horizontally for a selfie-view display.
            if self.settings['camera_mirror']:
                image = cv2.flip(image, 1)

            # -- POSE DETECTION ----------------
            # Detect pose landmarks from the current frame
            if self.mode == LIVE_STREAM:
                frame.flags.writeable = False
            self.results = pose.process(image)

            # Display Image for tracking window
            image = self.render_image(input_image)
            if self.results:
                image = self.tracking_preview(image)
            self.image = image
        else:
            if self.settings['camera_url']:
                error_camera_url(self.camera_setting)
            else:
                error_camera()
        return self.parameters

    def tracking_preview(self, image):
        # -- DRAW LANDMARKS --------
        if self.results.pose_world_landmarks:
            # Get coordinates
            self.parameters = self.results
            if self.mode == LIVE_STREAM:
                # Draw the pose annotation on the image.
                image.flags.writeable = True

            # Draw pose landmarks on the image.
            self.mp_drawing.draw_landmarks(
                image,
                self.parameters.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
        else:
            error_pose_estimation(image)
        return image

    def render_image(self, image):
        # -- Display the original input or an empty image as a base
        image = image.numpy_view()
        if self.settings['preview_enabled']:
            # Use the input image as a base if preview configuration is enabled
            image = np.copy(image)
            if self.settings['camera_mirror']:
                image = cv2.flip(image, 1)
        else:
            # Create an empty image with the same dimensions as the input image
            height, width, _ = image.shape
            image = np.zeros((height, width, 3), dtype=np.uint8)
        return image




