import asyncio
from plugin.connector import Connector
from plugin.pose_detection import PoseDetection
from plugin.mediapipe import get_bodyparts_values
import tkinter as tk
import threading
from plugin.ui import UI
import cv2
from info import VERSION


class Plugin:
    WINDOW_SIZE = "340x590"

    def __init__(self):
        self.settings = {}
        self.connected = False
        self.connector = None
        self.ui = None
        self.pose_detection = None

    async def run(self):
        # connection to software
        self.connector = Connector(self.settings['software'], self.settings['port'])
        if not self.connected:
            self.connected = await self.connector.connect()
            await self.connector.create_parameters()

        if self.connected and self.pose_detection:
            self.pose_detection.camera_connection()
            with self.pose_detection.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                # print('========== START LIVE TRACKING =========')
                while self.pose_detection.cap.isOpened():
                    parameters = self.pose_detection.detect(pose)
                    # - WINDOW : CAMERA TRACKING
                    cv2.imshow(f'VTS FullBody Tracking {VERSION}', self.pose_detection.image)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    if parameters:
                        data = get_bodyparts_values(parameters)
                        await self.connector.update_parameters(data)

    def update_tracking_window(self):
        if self.pose_detection.image != None:
            cv2.imshow(f'VTS FullBody Tracking {VERSION}', self.pose_detection.image)

    def start_tracking(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.run())
        loop.run_forever()

    def setup_ui(self):
        root = tk.Tk()
        root.title(f"VTS Fullbody Tracking {VERSION} - Settings")
        root.geometry(self.WINDOW_SIZE)
        root.configure(bg='#333333')

        ui = UI(root)
        ui.set_icons()
        ui.set_header()
        ui.set_available_cameras()
        ui.set_external_camera()
        ui.set_camera_view()
        ui.set_camera_mirror()
        ui.set_connection_software()
        ui.set_tracking_mode()

        def on_start():
            self.settings = ui.get_configuration()
            self.pose_detection = PoseDetection(self.settings)
            thread = threading.Thread(target=self.start_tracking)
            thread.daemon = True
            thread.start()
            # replace button 'start tracking' by button 'update'
            start_tracking_button.destroy()
            update_button = tk.Button(root, text="Update", command=on_update, font=('Arial', 14, 'bold'), bg='#07121d', fg='white', activebackground='#3c9fbb', activeforeground='white', bd=0)
            update_button.pack(pady=(5, 20), padx=20, fill=tk.X)

        # -- Start Tracking Button
        start_tracking_button = tk.Button(root, text="Start Tracking", command=on_start, font=('Arial', 14, 'bold'), bg='#07121d', fg='white', activebackground='#3c9fbb', activeforeground='white', bd=0)
        start_tracking_button.pack(pady=(5, 20), padx=20, fill=tk.X)

        def on_update():
            self.settings = ui.get_configuration()
            self.pose_detection.settings = self.settings

        root.mainloop()


def main():
    plugin = Plugin()
    plugin.setup_ui()


if __name__ == '__main__':
    main()
