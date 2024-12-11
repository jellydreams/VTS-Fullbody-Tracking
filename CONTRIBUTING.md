## DEVELOPMENT

Instructions for developers who want to run the plugin from the source code.

### Requirements

- Python 3.11

#### Install dependencies

```shell
pip install -r requirements.txt
```

**note**: The plugin use the method `vts.vts_request.requestSetMultiParameterValue` from the library pyvts. 
This method is not included in the latest released version 0.3.2. You will need it to run the plugin, which can be obtained from the current repository. Required method: https://github.com/Genteki/pyvts/blob/main/pyvts/vts_request.py l.246

### Run Plugin

- Open Vtube Studio
- Start the plugin

```shell
python app.py
```

### Build executable

```shell
 pyinstaller ./app.py -n VTS_Fullbody_Tracking-0.1.10 --add-data='models/*:models' --add-data="venv/Lib/site-packages/mediapipe/modules/pose_landmark/*:mediapipe/modules/pose_landmark" --add-data="venv/Lib/site-packages/mediapipe/modules/pose_detection/*:mediapipe/modules/pose_detection" --add-data='*.png:.' -F -w'
```


## Documentation

#### Mediapipe
mediapipe documentation -[Available Pose Landmarker models](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/index#models)<br/>
mediapipe documentation - [landmarker python](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python)<br/>
Blog Research Google - [On-device, Real-time Body Pose Tracking with MediaPipe BlazePose](https://blog.research.google/2020/08/on-device-real-time-body-pose-tracking.html)


#### VTube Studio

VTube Studio API: https://github.com/DenchiSoft/VTubeStudio

#### NizimaLIVE
nizima api: https://live2d-garage.github.io/<br/>
nizima Live API doc: https://github.com/Live2D/nizimaLIVEPluginAPI/tree/develop

#### Documentation Python Library
mediapipe: https://pypi.org/project/mediapipe/ <br/>
pyvts: https://genteki.github.io/pyvts/ <br/>
pyinstaller: https://pyinstaller.org/en/stable/ <br/>
pynizima: https://github.com/jellydreams/pyNizima