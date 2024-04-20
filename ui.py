from tkinter import ttk, Tk, Label, Button, BooleanVar, Checkbutton
import cv2


def get_available_cameras():
    """ Retrieves a list of connected cameras available for tracking """

    available_cameras = []

    # Check the first ten cameras
    for i in range(0, 10):
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
        camera_id = available_cameras[camera_index]['id']

        preview_enabled = preview_checkbox_var.get()
        return camera_id, preview_enabled

    root = Tk()
    root.title("Camera Selection")
    camera_label = Label(root, text="Select Camera:")
    camera_label.pack()

    # -- Camera Selection
    available_cameras = get_available_cameras()
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

    # -- Submit Configuration
    start_button = Button(root, text="Start Tracking", command=root.quit)
    start_button.pack()

    root.mainloop()

    tracking_configuration = get_configuration()

    return root, tracking_configuration
