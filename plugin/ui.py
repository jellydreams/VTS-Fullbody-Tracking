import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from info import VERSION, ICON_PATH
import os

import platform
import subprocess

BACKGROUND_COLOR = "#333333"
TEXT_COLOR = "white"

BACKGROUND_VTUBE_STUDIO = '#fb58bb'
BACKGROUND_NIZIMA = '#692fc9'

WINDOW_SIZE = "340x440"

NIZIMA_LIVE = 'NizimaLIVE'
VTUBE_STUDIO = 'VTube Studio'


ICON_NIZIMA = 'icon_nizimalive.png'
ICON_VTUBE_STUDIO = 'icon_vtubestudio.png'

icon_nizima = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_NIZIMA))
icon_nizima = Image.open(icon_nizima.replace("plugin\\", ""))



def window_tracking_configuration():
    """ Window for choosing configuration for tracking """

    def get_configuration():
        """ Retrieves configuration values from UI form """
        camera_url = camera_url_entry.get()
        software = selected_software.get()
        api_port = nizima_port_input.get() if software == NIZIMA_LIVE else vtube_port_input.get()
        if not api_port:
            if software == NIZIMA_LIVE:
                api_port = 22022
            else:
                api_port = 8001

        settings = {
            'camera_url': camera_url,
            'preview_enabled': show_camera_view_var.get(),
            'port': api_port,
            'software': software
        }

        if available_cameras:
            camera_name = camera_selection.get()
            camera_index = camera_options.index(camera_name)
            settings['camera_id'] = available_cameras[camera_index]['id']

        return settings

    def toggle_inputs():
        """Enable or disable the input fields based on the selected software."""
        if selected_software.get() == VTUBE_STUDIO:
            # Enable VTube Studio inputs
            vtube_port_input.config(state="normal")
            vtube_port_label.config(fg="white")
            vtube_name_label.config(fg="white")

            # Disable NizimaLive inputs
            nizima_port_input.config(state="disabled")
            nizima_port_label.config(fg="gray")
            nizima_name_label.config(fg="gray")
        elif selected_software.get() == NIZIMA_LIVE:
            # Enable NizimaLive inputs
            nizima_port_input.config(state="normal")
            nizima_port_label.config(fg="white")
            nizima_name_label.config(fg="white")

            # Disable VTube Studio inputs
            vtube_port_input.config(state="disabled")
            vtube_port_label.config(fg="gray")
            vtube_name_label.config(fg="gray")

    root = tk.Tk()
    root.title(f"VTS Fullbody Tracking {VERSION} - Settings")
    root.geometry(WINDOW_SIZE)
    root.configure(bg='#333333')

    # Set window icon
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_PATH))
    icon_image = Image.open(icon_path.replace("plugin\\", ""))
    icon_resized_for_window = icon_image.resize((32, 32))
    window_icon = ImageTk.PhotoImage(icon_resized_for_window)
    root.iconphoto(False, window_icon)

    # -- Header
    header_frame = tk.Frame(root, bg='#222222')
    header_frame.pack(fill=tk.X)

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
    else:
        camera_label = tk.Label(root, text="No camera found\n Connect a camera before running the plugin")
        camera_label.pack()

    # Camera external connection
    camera_url_frame = tk.Frame(root, bg='#333333')
    camera_url_frame.pack(pady=(10, 20), padx=20, fill=tk.X)
    camera_url_label = tk.Label(camera_url_frame, text="Camera url", bg='#333333', fg='white', font=('Arial', 10))
    camera_url_label.pack(side=tk.LEFT, padx=5)
    camera_url_entry = tk.Entry(camera_url_frame, validate="key", font=('Arial', 10), width=30)
    camera_url_entry.pack(side=tk.LEFT, fill=tk.X)

    # Option for showing original input when displaying tracking pose
    show_camera_view_var = tk.BooleanVar()
    show_camera_view_checkbox = tk.Checkbutton(root, text="Show Camera View", variable=show_camera_view_var, bg='#333333', fg='white',  activeforeground='white', activebackground="#333333",  selectcolor='black', font=('Arial', 10))
    show_camera_view_checkbox.pack(anchor='w', padx=20, pady=(0, 10))

    # -- Vtube Studio Settings
    vtube_studio_frame = create_section_header(root, "Connection Settings")
    vtube_studio_frame.pack(fill=tk.X, pady=(0, 5))

    # --------------
    # Use ttk to add styling to button
    style = ttk.Style(root)
    style.configure('TButton', bg='skyblue', fg='white')

    # Chargement des icônes
    image = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_VTUBE_STUDIO))
    image = Image.open(image.replace("plugin\\", ""))
    image_resized = image.resize((25, 25))
    vtube_icon = ImageTk.PhotoImage(image_resized)
    # Charger l'image avec Pillow

    image = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_NIZIMA))
    image = Image.open(image.replace("plugin\\", ""))
    image_resized = image.resize((25, 25))
    nizima_icon = ImageTk.PhotoImage(image_resized)  # Remplacez avec le chemin correct

    # Variable to track the selected software
    selected_software = tk.StringVar(value=VTUBE_STUDIO)

    # Main frame
    main_frame = tk.Frame(root, padx=10, pady=10, bg=BACKGROUND_COLOR)
    main_frame.pack()

    # Row for VTube Studio
    vtube_row = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    vtube_row.pack(anchor="w", pady=5)

    vtube_radio = tk.Radiobutton(vtube_row, variable=selected_software, value=VTUBE_STUDIO, command=toggle_inputs, bg=BACKGROUND_COLOR )

    vtube_radio.pack(side="left", padx=5)

    vtube_icon_label = tk.Label(vtube_row, image=vtube_icon, bg=BACKGROUND_COLOR, width=18)
    vtube_icon_label.pack(side="left", padx=5)

    vtube_name_label = tk.Label(vtube_row, text=VTUBE_STUDIO, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=12)
    vtube_name_label.pack(side="left", padx=5)

    vtube_port_label = tk.Label(vtube_row, text="Port:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    vtube_port_label.pack(side="left", padx=5)

    vtube_port_input = tk.Entry(vtube_row, width=10)
    vtube_port_input.pack(side="left", padx=5)
    vtube_port_input.insert(0, "8001")  # Default port

    # Row for NizimaLive
    nizima_row = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    nizima_row.pack(anchor="w", pady=5)

    nizima_radio = tk.Radiobutton(nizima_row, variable=selected_software, value=NIZIMA_LIVE, command=toggle_inputs, bg=BACKGROUND_COLOR)
    nizima_radio.pack(side="left", padx=5)

    nizima_icon_label = tk.Label(nizima_row, image=nizima_icon, bg=BACKGROUND_COLOR, width=18)
    nizima_icon_label.pack(side="left", padx=5)

    nizima_name_label = tk.Label(nizima_row, text=NIZIMA_LIVE, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=12)
    nizima_name_label.pack(side="left", padx=5)

    nizima_port_label = tk.Label(nizima_row, text="Port:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
    nizima_port_label.pack(side="left", padx=5)

    nizima_port_input = tk.Entry(nizima_row, width=10)
    nizima_port_input.pack(side="left", padx=5)
    nizima_port_input.insert(0, "22022")  # Default port

    # Initialiser les états des champs
    toggle_inputs()

    # -- Start Tracking Button
    start_tracking_button = tk.Button(root, text="Start Tracking", command=root.quit, font=('Arial', 14, 'bold'), bg='#07121d', fg='white', activebackground='#3c9fbb', activeforeground='white', bd=0)
    start_tracking_button.pack(pady=(5, 20), padx=20, fill=tk.X)

    root.mainloop()

    tracking_configuration = get_configuration()

    return root, tracking_configuration


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
