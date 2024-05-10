from tkinter import ttk, Tk, Label, Button, BooleanVar, Checkbutton, Entry, Frame, LEFT, RIGHT
import cv2

from info import VERSION


def get_available_cameras():
    """ Retrieves a list of connected cameras available for tracking """

    available_cameras = []

    # Check the first 20 cameras
    for i in range(0, 20):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            _, name = cap.read()
            if not name is None:
                # TODO: Retrieve system names for cameras
                available_cameras.append({'label': f"Camera {i}: {name.shape[1]}x{name.shape[0]}", 'id': i})
            cap.release()

    return available_cameras


def window_tracking_configuration():
    """ Window for choosing configuration for tracking """

    def get_configuration():
        """ Retrieves configuration values from UI form """
        camera_name = camera_combobox.get()
        camera_index = camera_options.index(camera_name)

        port = port_entry.get()

        settings = {
            'camera_id': available_cameras[camera_index]['id'],
            'preview_enabled': preview_checkbox_var.get(),
            'port': port if port else 8001
        }

        return settings

    root = Tk()
    root.title(f"VTS Fullbody Tracking {VERSION} - Settings")

    title = Label(root, text=f"VTS Fullbody Tracking {VERSION}")
    title.pack()

    available_cameras = get_available_cameras()

    if available_cameras:
        # -- Camera Selection
        camera_label = Label(root, text="Select Camera:")
        camera_label.pack()
        camera_options = [info['label'] for info in available_cameras]
        camera_combobox = ttk.Combobox(root, values=camera_options, state="readonly")
        camera_combobox.current(0)  # Sélect first camera by default
        camera_combobox.pack()

        camera_label = Label(root, text="Tracking Preview Options ")
        camera_label.pack()

        # -- Option for showing original input when displaying tracking pose
        preview_checkbox_var = BooleanVar()
        preview_checkbox = Checkbutton(root, text="Show Camera View", variable=preview_checkbox_var)
        preview_checkbox.pack()

        # -- Custom Port Entry
        port_frame = Frame(root)
        port_frame.pack(anchor="w", pady=(10, 0))

        port_label = Label(port_frame, text="API Port:")
        port_label.pack(side=LEFT)

        vcmd = root.register(validate_port_input)
        port_entry = Entry(port_frame, validate="key", validatecommand=(vcmd, '%P'), width=10)
        port_entry.insert(0, "8001")  # Default value
        port_entry.pack(side=RIGHT)

        # -- Submit Configuration
        start_button = Button(root, text="Start Tracking", command=root.quit)
        start_button.pack()
    else:
        camera_label = Label(root, text="No camera found\n Connect a camera before running the plugin")
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