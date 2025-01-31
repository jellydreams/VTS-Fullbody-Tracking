import pyvts
import cv2
import os

from pynizima import NizimaRequest
from pynizima.errors import InvalidToken
from info import VERSION, ICON_PATH

from .mediapipe import get_parameters_names
from plugin.errors_ui import error_connection_vts

NIZIMA_LIVE = 'NizimaLIVE'
VTUBE_STUDIO = 'VTube Studio'


icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../icon.png'))

plugin_info = {
    "plugin_name": "VTS_Fullbody_Tracking",
    "developer": "JellyDreams",
    "authentication_token_path": "./token.txt",
    "plugin_icon": icon_path
}

vts_api = {"version": "1.0", "name": "VTubeStudioPublicAPI", "port": 8001}


class Connector:

    def __init__(self, software, port=8001):
        self.software = software
        self.connector = None
        self.port = port
        self.connection = False

    async def connect(self):
        if self.software == NIZIMA_LIVE:
            plugin_infos = {
                "Name": 'Fullbody Tracking',
                "Developer": 'Jelly Dreams'
            }
            self.connector = Nizima(plugin_infos=plugin_infos, port=self.port)
            await self.connector.connect_nizima()
            self.connection = True

        # ----- VTUBE STUDIO -------------
        elif self.software == VTUBE_STUDIO:
            vts_api['port'] = self.port
            self.connector = pyvts.vts(plugin_info=plugin_info, vts_api_info=vts_api)

            try:
                await connection_vts(self.connector)
                self.connection = True
            except ConnectionError:
                error_connection_vts()
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        return self.connection

    async def create_parameters(self):
        if self.software == NIZIMA_LIVE:
            if self.connector.connection:
                await self.connector.create_parameters()
        elif self.software == VTUBE_STUDIO:
            await create_parameters_vts(self.connector)

    async def update_parameters(self, data):
        if self.software == NIZIMA_LIVE:
            data = [{"Id": key, "Value": value * 10} for key, value in data.items()]
            await self.connector.set_live_parameter_values(data)
        elif self.software == VTUBE_STUDIO:
            # Prepare values to send
            names, values = zip(*data.items())
            await send_paramters_vts(self.connector, values, names)


async def connection_vts(vts):
    # Initialize VTube Studio connection
    await vts.connect()
    # Authenticate with VTube Studio API
    # print('authentification VtubeStudio..')
    await vts.request_authenticate_token()  # get token
    await vts.request_authenticate()  # use token


async def create_parameters_vts(vts):
    # print('Create parameters in VTube Studio')
    # Prepare parameter names for each body part
    parameter_names = get_parameters_names()
    for parameter_name in parameter_names:
        # Add custom parameters in VTube Studio
        send_request_new_parameter = vts.vts_request.requestCustomParameter(parameter_name, min=-10, max=10)
        await vts.request(send_request_new_parameter)


async def send_paramters_vts(vts, values, names):
    """parameters in VTube Studio """
    send_request_parameter = vts.vts_request.requestSetMultiParameterValue(names, values, weight=1, face_found=True, mode='set')
    await vts.request(send_request_parameter)


class Nizima(NizimaRequest):

    def __init__(self, plugin_infos, token_path='token-fullbodytracking.txt', **kwargs):
        self.plugin_infos = plugin_infos
        self.plugin_name = plugin_infos['Name']
        self.token = ''
        self.token_path = token_path
        self.connection = False
        NizimaRequest.__init__(self, **kwargs)

    async def connect_nizima(self):
        self.token = self.load_token()
        # no token : register plugin and save token
        if not self.token:
            await self.register_plugin()

        # connect to nizima
        while not self.connection:
            try:
                enabled = await self.establish_connection()
                # if user delete plugin in nizima, user would need a new token (if old token will make an invalidMethod
                if enabled:
                    self.connection = True
                    return True
            except InvalidToken:
                # if user delete plugin in nizima, user would need a new token
                await self.register_plugin()

        return False

    async def establish_connection(self, **kwargs):
        enabled = await super().establish_connection(name=self.plugin_name, token=self.token, version=VERSION)
        return enabled

    async def register_plugin(self, **kwargs):
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ICON_PATH)).replace("plugin\\", "")
        self.token = await super().register_plugin(name=self.plugin_name, developer=self.plugin_infos['Developer'], version=VERSION, icon=icon_path)
        self.save_token(self.token)
        return self.token

    async def create_parameters(self):
        # print('Create parameters in VTube Studio')

        # Prepare parameter names for each body part
        parameter_names = get_parameters_names()
        parameters = []
        # Maximum of 100 parameters allowed to be created in VTube Studio per plugin
        for parameter_name in parameter_names:
            parameter = {
                "Id": parameter_name,
                "Group": self.group_name(parameter_name),
                "Base": 0,
                "Max": 10,
                "Min": -10,
                # 'Repeat' : Boolean
            }
            parameters.append(parameter)
            # Add custom parameters in VTube Studio

        await self.insert_live_parameters(parameters)

    def save_token(self, token):
        """
        Save a token to a file.
        :param token: The token to save (string).
        """
        with open(self.token_path, 'w') as file:
            file.write(token)

    def load_token(self):
        """
        Retrieve a token from a file. Load the existing token if available
        :return: The retrieved token (string) or None if the file does not exist.
        """
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as file:
                return file.read().strip()
        else:
            print(f"File not found: {self.token_path}")
            return None

    def group_name(self, input_name):
        group = input_name
        group.replace('RIGHT', 'R')
        group.replace('LEFT', 'L')
        group = group.split('_')
        group.remove(group[-1])  # remove axis info
        group_name = ' '.join([text.capitalize() for text in group])
        return group_name
