# VTS FULLBODY TRACKING

🔗 website: [vts-fullbody-tracking.gitlab.io](https://vts-fullbody-tracking.gitlab.io/) 

[discord-link]: https://discord.gg/9K9gejWQ3s

[![Last Release][github-release-badge]](https://github.com/jellydreams/VTS-Fullbody-Tracking/releases)
[![VTS FULLBODY TRACKING Discord][discord-badge]](https://discord.gg/9K9gejWQ3s)
[![Twitter Follow][twitter-badge]](https://twitter.com/_JellyDreams_)

[discord-badge]: https://img.shields.io/badge/Join_Discord-indigo?logo=discord&logoColor=white&color=7289da
[twitter-badge]: https://img.shields.io/twitter/follow/_JellyDreams_.svg?style=social
[github-release-badge]: https://img.shields.io/github/v/release/jellydreams/VTS-Fullbody-Tracking?label=ALPHA%20release

This plugin integrates full body tracking functionality using Mediapipe. 
It allows users to use tracked body parameters as inputs to control Live2D model in [VTube Studio](https://denchisoft.com/). 

![Demo Tracking Arms](readme_img/Demo_Tracking_Arms.png)

## THIS PLUGIN IS UNDER DEVELOPMENT
This plugin may contain bugs and lack certain features.<br>
Visit the [Wiki](https://github.com/jellydreams/VTS-Fullbody-Tracking/wiki) or [Website](https://vts-fullbody-tracking.gitlab.io/) for more information on how the plugin works. <br>
Join [Discord Server](https://discord.gg/9K9gejWQ3s) to share tests and feedbacks, ask questions or get help.

### How you can Help
- **Live2D Rigger**: Help understand how to effectively rig models for the body parts feature
- **Live2D Vtuber**: Experiment with usability and performance for movement and configuration in VTube Studio
- **Developper**: Contributions are welcome to improve this plugin

### Troubleshooting
- Currently, there might be a latency of a few seconds
- Tracking input may be inaccurate and exhibit occasional jumps

## Run the Plugin

**Requirements**: Window, VTube Studio, Camera

1. Download the executable from the [releases page](https://github.com/jellydreams/VTS-Fullbody-Tracking/releases)
2. **Connect a Camera** and **Open VTube Studio.**
4. **Double-click on the executable file** `VTS_Fullbody_Tracking.exe` to launch the plugin. A settings window will appear.
5.  **Select your camera** and **click on the 'Start Tracking' button**
6. **Allow the plugin in vtube Studio**. Window displaying a preview of pose tracking will appear.
7. **Configure your model's parameter settings**, using plugin parameters as inputs. you can now choose body parts X, Y, Z coordinates, and visibility as inputs

📖 Wiki Section - [Run the plugin](https://github.com/jellydreams/VTS-Fullbody-Tracking/wiki/Run-the-plugin)

## Settings

### Peview Camera
Displays the image captured by the camera

| default                                                  | Preview Camera                                                       | 
|----------------------------------------------------------|----------------------------------------------------------------------|
| ![exemple_preview.png](readme_img/exemple_preview.png)   | ![exemple_camera_preview.png](readme_img/exemple_camera_preview.png) | 

📖Wiki Section - [Settings Window](https://github.com/jellydreams/VTS-Fullbody-Tracking/wiki/Settings-Window)

## Custom Parameters
This plugin add new controls for various body parts in Vtube Studio. \
Each body part has parameters for controlling its position and visibility.

![List Bodyparts MediaPipe](readme_img/list_bodyparts.png)<br/>

- **Arms**: Shoulders, Elbow, Wrists
- **Torso**: Clavicles, Hips
- **Legs**: Knees, Ankles
- **Feet**: Heels, Feet Index
- **Hands**: Pinkies Knuckles, Index Knuckles, Thumb Knuckles

📖Wiki Section - [List of Parameters](https://github.com/jellydreams/VTS-Fullbody-Tracking/wiki/Custom-Parameters)

___

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
 pyinstaller ./app.py -n VTS_Fullbody_Tracking-0.1.8 --add-data='models/*:models' --add-data='icon.png:.' -F -w 
```

## Documentation

#### Mediapipe
mediapipe documentation -[Available Pose Landmarker models](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/index#models)<br/>
mediapipe documentation - [landmarker python](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python)<br/>
Blog Research Google - [On-device, Real-time Body Pose Tracking with MediaPipe BlazePose](https://blog.research.google/2020/08/on-device-real-time-body-pose-tracking.html)


#### VTube Studio

VTube Studio API: https://github.com/DenchiSoft/VTubeStudio

#### Documentation Python Library
mediapipe: https://pypi.org/project/mediapipe/ <br/>
pyvts: https://genteki.github.io/pyvts/ <br/>
pyinstaller: https://pyinstaller.org/en/stable/



