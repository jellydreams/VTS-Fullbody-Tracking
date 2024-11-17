import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from info import VERSION, ICON_PATH
import os

import platform
import subprocess


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


def window_tracking_configuration():
    """ Window for choosing configuration for tracking """

    def get_configuration():
        """ Retrieves configuration values from UI form """
        camera_name = camera_selection.get()
        camera_index = camera_options.index(camera_name)

        port = api_port_entry.get()

        settings = {
            'camera_id': available_cameras[camera_index]['id'],
            'preview_enabled': show_camera_view_var.get(),
            'port': port if port else 8001
        }

        return settings

    root = tk.Tk()
    root.title(f"VTS Fullbody Tracking {VERSION} - Settings")
    root.geometry("340x340")
    root.configure(bg='#333333')

    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_PATH))
    icon_image = Image.open(icon_path)

    # Set window icon
    icon_resized_for_window = icon_image.resize((32, 32))
    window_icon = ImageTk.PhotoImage(icon_resized_for_window)
    root.iconphoto(False, window_icon)

    # -- Header
    header_frame = tk.Frame(root, bg='#222222')
    header_frame.pack(fill=tk.X)
    # Plugin Icon
    # Load and resize icon image for window and header
    icon_photo = icon_image.resize((50, 50))
    icon_photo = ImageTk.PhotoImage(icon_photo)
    icon_label = tk.Label(header_frame, image=icon_photo, bg='#222222')
    icon_label.pack(side=tk.LEFT, padx=10, pady=10)
    # Plugin name
    title_label = tk.Label(header_frame, text="VTS Fullbody Tracking", bg='#222222', fg='white', font=('Arial', 12, 'bold'))
    title_label.pack(padx=10, pady=(15, 2))
    # version
    version_label = tk.Label(header_frame, text=f"version {VERSION}", bg='#222222', fg='#bfbfbf', font=('Arial', 8))
    version_label.pack(padx=10)

    available_cameras = get_available_cameras()

    if available_cameras:
        # -- Camera Settings
        camera_options = [info['label'] for info in available_cameras]
        camera_settings_frame = create_section_header(root, "Camera Settings")
        camera_settings_frame.pack(fill=tk.X, pady=(0, 5))

        # Camera Selection
        camera_selection = ttk.Combobox(root, values=camera_options, state='readonly', font=('Arial', 10))
        camera_selection.current(0)
        camera_selection.pack(pady=(10, 5), padx=20, fill=tk.X)

        # Option for showing original input when displaying tracking pose
        show_camera_view_var = tk.BooleanVar()
        show_camera_view_checkbox = tk.Checkbutton(root, text="Show Camera View", variable=show_camera_view_var, bg='#333333', fg='white',  activeforeground='white', activebackground="#333333",  selectcolor='black', font=('Arial', 10))
        show_camera_view_checkbox.pack(anchor='w', padx=20, pady=(0, 10))

        # -- Vtube Studio Settings
        vtube_studio_frame = create_section_header(root, "Vtube Studio Settings")
        vtube_studio_frame.pack(fill=tk.X, pady=(0, 5))

        # Custom Port Entry
        api_port_frame = tk.Frame(root, bg='#333333')
        api_port_frame.pack(pady=(10, 20), padx=20, fill=tk.X)
        api_port_label = tk.Label(api_port_frame, text="API Port:", bg='#333333', fg='white', font=('Arial', 10))
        api_port_label.pack(side=tk.LEFT, padx=5)
        vcmd = root.register(validate_port_input)
        api_port_entry = tk.Entry(api_port_frame, validate="key", validatecommand=(vcmd, '%P'), font=('Arial', 10), width=10)
        api_port_entry.insert(0, "8001")
        api_port_entry.pack(side=tk.LEFT, fill=tk.X)

        # -- Start Tracking Button
        start_tracking_button = tk.Button(root, text="Start Tracking", command=root.quit, font=('Arial', 14, 'bold'), bg='#07121d', fg='white', activebackground='#3c9fbb', activeforeground='white', bd=0)
        start_tracking_button.pack(pady=(5, 20), padx=20, fill=tk.X)

    else:
        camera_label = tk.Label(root, text="No camera found\n Connect a camera before running the plugin")
        camera_label.pack()

    root.mainloop()

    tracking_configuration = get_configuration()

    return root, tracking_configuration


def validate_port_input(new_value):
    """ Validate port input """
    if new_value.isdigit() and int(new_value) >= 0:
        return True
    elif new_value == "":
        return True
    else:
        return False
