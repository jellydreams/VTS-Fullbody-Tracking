import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import platform
import subprocess

from info import VERSION, ICON_PATH
from plugin.connector import VTUBE_STUDIO, NIZIMA_LIVE
from plugin.mediapipe import LIVE_STREAM, IMAGE

BACKGROUND_COLOR = "#333333"
TEXT_COLOR = "white"

BACKGROUND_VTUBE_STUDIO = '#fb58bb'
BACKGROUND_NIZIMA = '#692fc9'


class UI:
    def __init__(self, root):
        self.root = root

        self.camera_url_entry = None
        self.selected_software = None
        self.nizima_port_input = None
        self.vtube_port_input = None
        self.selected_tracking_mode = None
        self.show_camera_view_var = None
        self.camera_mirror_var = None
        self.camera_selection = None
        self.available_cameras = None
        self.camera_options = None

        self.icon_photo = None
        self.nizima_icon = None
        self.vtube_studio_icon = None

    def get_configuration(self):
        """ Retrieves configuration values from UI form """
        camera_url = self.camera_url_entry.get()
        software = self.selected_software.get()
        api_port = self.nizima_port_input.get() if software == NIZIMA_LIVE else self.vtube_port_input.get()
        if not api_port:
            if software == NIZIMA_LIVE:
                api_port = 22022
            else:
                api_port = 8001
        tracking_mode = self.selected_tracking_mode.get()

        settings = {
            'camera_url': camera_url,
            'preview_enabled': self.show_camera_view_var.get(),
            'camera_mirror': self.camera_mirror_var.get(),
            'port': api_port,
            'software': software,
            'tracking_mode': tracking_mode
        }

        if self.available_cameras:
            camera_name = self.camera_selection.get()
            camera_index = self.camera_options.index(camera_name)
            settings['camera_id'] = self.available_cameras[camera_index]['id']

        return settings

    def set_icons(self):
        # Set window icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_PATH))
        icon_image = Image.open(icon_path.replace("plugin\\", ""))
        icon_resized_for_window = icon_image.resize((32, 32))
        window_icon = ImageTk.PhotoImage(icon_resized_for_window)
        self.root.iconphoto(False, window_icon)

    def set_header(self):
        header_frame = tk.Frame(self.root, bg='#222222')
        header_frame.pack(fill=tk.X)

        # Load and resize icon image for window and header
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_PATH))
        icon_image = Image.open(icon_path.replace("plugin\\", ""))
        icon_photo = icon_image.resize((50, 50))
        self.icon_photo = ImageTk.PhotoImage(icon_photo)
        icon_label = tk.Label(header_frame, image=self.icon_photo, bg='#222222')
        icon_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Plugin name
        title_label = tk.Label(header_frame, text="VTS Fullbody Tracking", bg='#222222', fg='white', font=('Arial', 12, 'bold'))
        title_label.pack(padx=10, pady=(15, 2))
        # version
        version_label = tk.Label(header_frame, text=f"version {VERSION}", bg='#222222', fg='#bfbfbf', font=('Arial', 8))
        version_label.pack(padx=10)

    def set_available_cameras(self):
        self.available_cameras = get_available_cameras()

        if self.available_cameras:
            # -- Camera Settings
            self.camera_options = [info['label'] for info in self.available_cameras]
            camera_settings_frame = create_section_header(self.root, "Camera Settings")
            camera_settings_frame.pack(fill=tk.X, pady=(0, 5))

            # Camera Selection
            self.camera_selection = ttk.Combobox(self.root, values=self.camera_options, state='readonly', font=('Arial', 10))
            self.camera_selection.current(0)
            self.camera_selection.pack(pady=(10, 5), padx=20, fill=tk.X)
        else:
            camera_label = tk.Label(self.root, text="No camera found\n Connect a camera before running the plugin")
            camera_label.pack()

    def set_external_camera(self):
        # Camera external connection
        camera_url_frame = tk.Frame(self.root, bg='#333333')
        camera_url_frame.pack(pady=(10, 20), padx=20, fill=tk.X)
        camera_url_label = tk.Label(camera_url_frame, text="Camera url", bg='#333333', fg='white', font=('Arial', 10))
        camera_url_label.pack(side=tk.LEFT, padx=5)
        self.camera_url_entry = tk.Entry(camera_url_frame, validate="key", font=('Arial', 10), width=30)
        self.camera_url_entry.pack(side=tk.LEFT, fill=tk.X)

    def set_camera_view(self):
        # Option for showing original input when displaying tracking pose
        self.show_camera_view_var = tk.BooleanVar()
        show_camera_view_checkbox = tk.Checkbutton(self.root, text="Show Camera View", variable=self.show_camera_view_var, bg='#333333', fg='white', activeforeground='white', activebackground="#333333", selectcolor='black', font=('Arial', 10))
        show_camera_view_checkbox.pack(anchor='w', padx=20, pady=(0, 10))

    def set_camera_mirror(self):
        # Option for showing original input when displaying tracking pose
        self.camera_mirror_var = tk.BooleanVar()
        camera_mirror_checkbox = tk.Checkbutton(self.root, text="Mirror Camera", variable=self.camera_mirror_var, bg='#333333', fg='white', activeforeground='white', activebackground="#333333", selectcolor='black', font=('Arial', 10))
        camera_mirror_checkbox.pack(anchor='w', padx=20, pady=(0, 10))

    def set_connection_software(self):
        ICON_NIZIMA = 'icon_nizimalive.png'
        ICON_VTUBE_STUDIO = 'icon_vtubestudio.png'

        # -- Vtube Studio Settings
        vtube_studio_frame = create_section_header(self.root, "Connection Settings")
        vtube_studio_frame.pack(fill=tk.X, pady=(0, 5))

        # --------------
        def toggle_inputs():
            """Enable or disable the input fields based on the selected software."""
            if self.selected_software.get() == VTUBE_STUDIO:
                # Enable VTube Studio inputs
                self.vtube_port_input.config(state="normal")
                vtube_port_label.config(fg="white")
                vtube_name_label.config(fg="white")

                # Disable NizimaLive inputs
                self.nizima_port_input.config(state="disabled")
                nizima_port_label.config(fg="gray")
                nizima_name_label.config(fg="gray")
            elif self.selected_software.get() == NIZIMA_LIVE:
                # Enable NizimaLive inputs
                self.nizima_port_input.config(state="normal")
                nizima_port_label.config(fg="white")
                nizima_name_label.config(fg="white")

                # Disable VTube Studio inputs
                self.vtube_port_input.config(state="disabled")
                vtube_port_label.config(fg="gray")
                vtube_name_label.config(fg="gray")

        # load vtube studio icon
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_VTUBE_STUDIO))
        image = Image.open(image.replace("plugin\\", ""))
        image_resized = image.resize((25, 25))
        self.vtube_studio_icon = ImageTk.PhotoImage(image_resized)

        # load nizima icon
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_NIZIMA))
        image = Image.open(image.replace("plugin\\", ""))
        image_resized = image.resize((25, 25))
        self.nizima_icon = ImageTk.PhotoImage(image_resized)

        # Variable to track the selected software
        self.selected_software = tk.StringVar(value=VTUBE_STUDIO)

        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10, bg=BACKGROUND_COLOR)
        main_frame.pack()

        # Row for VTube Studio
        vtube_row = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        vtube_row.pack(anchor="w", pady=5)

        vtube_radio = tk.Radiobutton(vtube_row, variable=self.selected_software, value=VTUBE_STUDIO, command=toggle_inputs,
                                     bg=BACKGROUND_COLOR)
        vtube_radio.pack(side="left", padx=5)

        vtube_icon_label = tk.Label(vtube_row, image=self.vtube_studio_icon, bg=BACKGROUND_COLOR, width=18)
        vtube_icon_label.pack(side="left", padx=5)

        vtube_name_label = tk.Label(vtube_row, text=VTUBE_STUDIO, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=12)
        vtube_name_label.pack(side="left", padx=5)

        vtube_port_label = tk.Label(vtube_row, text="Port:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        vtube_port_label.pack(side="left", padx=5)

        self.vtube_port_input = tk.Entry(vtube_row, width=10)
        self.vtube_port_input.pack(side="left", padx=5)
        self.vtube_port_input.insert(0, "8001")  # Default port

        # Row for NizimaLive
        nizima_row = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        nizima_row.pack(anchor="w", pady=5)

        nizima_radio = tk.Radiobutton(nizima_row, variable=self.selected_software, value=NIZIMA_LIVE, command=toggle_inputs, bg=BACKGROUND_COLOR)
        nizima_radio.pack(side="left", padx=5)

        nizima_icon_label = tk.Label(nizima_row, image=self.nizima_icon, bg=BACKGROUND_COLOR, width=18)
        nizima_icon_label.pack(side="left", padx=5)

        nizima_name_label = tk.Label(nizima_row, text=NIZIMA_LIVE, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=12)
        nizima_name_label.pack(side="left", padx=5)

        nizima_port_label = tk.Label(nizima_row, text="Port:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        nizima_port_label.pack(side="left", padx=5)

        self.nizima_port_input = tk.Entry(nizima_row, width=10)
        self.nizima_port_input.pack(side="left", padx=5)
        self.nizima_port_input.insert(0, "22022")  # Default port

        # Init state fields
        toggle_inputs()

    def set_tracking_mode(self):
        def toggle_inputs_tracking_mode():
            """Enable or disable the input fields based on the selected software."""
            if self.selected_tracking_mode.get() == LIVE_STREAM:
                mode_live_stream_label.config(fg="white")
                mode_image_label.config(fg="gray")
            elif self.selected_tracking_mode.get() == IMAGE:
                mode_image_label.config(fg="white")
                mode_live_stream_label.config(fg="gray")

        # -- Tracking mode
        tracking_setting_frame = create_section_header(self.root, "Tracking Settings")
        tracking_setting_frame.pack(fill=tk.X, pady=(0, 5))

        # Variable to track the selected software
        self.selected_tracking_mode = tk.StringVar(value=LIVE_STREAM)

        tracking_mode_frame = tk.Frame(self.root, padx=30, bg=BACKGROUND_COLOR)
        tracking_mode_frame.pack(anchor="w", pady=5)

        live_stream_row = tk.Frame(tracking_mode_frame, bg=BACKGROUND_COLOR)
        live_stream_row.pack(anchor="w", pady=5)
        mode_live_stream_radio = tk.Radiobutton(live_stream_row, variable=self.selected_tracking_mode, value=LIVE_STREAM, command=toggle_inputs_tracking_mode, bg=BACKGROUND_COLOR)
        mode_live_stream_radio.pack(side="left", padx=5)
        mode_live_stream_label = tk.Label(live_stream_row, text="Smooth (Slower)", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        mode_live_stream_label.pack(side="left", padx=5)

        image_row = tk.Frame(tracking_mode_frame, bg=BACKGROUND_COLOR)
        image_row.pack(anchor="w", pady=5)
        mode_image_radio = tk.Radiobutton(image_row, variable=self.selected_tracking_mode, value=IMAGE, command=toggle_inputs_tracking_mode, bg=BACKGROUND_COLOR)
        mode_image_radio.pack(side="left", padx=5)
        mode_image_label = tk.Label(image_row, text="Fast (Less Stable)", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        mode_image_label.pack(side="left", padx=5)
        toggle_inputs_tracking_mode()


def get_available_cameras_names():
    available_cameras = {}

    if (platform.system() == "Windows") and not ("WINEPREFIX" in os.environ):
        from pygrabber.dshow_graph import FilterGraph
        devices = FilterGraph().get_input_devices()

        for device_index, device_name in enumerate(devices):
            available_cameras[device_index] = device_name
    else:
        # Retrieve camera names using system_profiler on macOS
        try:
            # Execute the command to get video devices
            result = subprocess.run(
                ["system_profiler", "SPCameraDataType"],
                stdout=subprocess.PIPE,
                text=True
            )
            output = result.stdout

            # Search for camera names in the output
            lines = output.split("\n")
            camera_index = 0
            for line in lines:
                if "Model ID:" in line or "Camera Model ID:" in line:  # Check for the model name
                    camera_name = line.split(":")[1].strip()
                    available_cameras[camera_index] = camera_name
                    camera_index += 1

        except Exception as e:
            print(f"Error while retrieving cameras: {e}")

    return available_cameras


def get_available_cameras():
    """ Retrieves a list of connected cameras available for tracking """

    available_cameras = []
    names = get_available_cameras_names()

    for i in names:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            _, name = cap.read()
            if not name is None:
                available_cameras.append({'label': f"Camera {i}: {names[i]} {name.shape[1]}x{name.shape[0]}", 'id': i})
            cap.release()

    return available_cameras


def create_section_header(root, text):
    """ Create section headers with background """
    frame = tk.Frame(root, bg='#444444')
    label = tk.Label(frame, text=text, bg='#444444', fg='white', font=('Arial', 10, 'bold'))
    label.pack(pady=5, padx=10, anchor='w')
    return frame


def validate_port_input(new_value):
    """ Validate port input """
    if new_value.isdigit() and int(new_value) >= 0:
        return True
    elif new_value == "":
        return True
    else:
        return False
