import os

from plugin.mediapipe import get_parameters_names
from pynizima import NizimaRequest
from pynizima.errors import InvalidToken
from info import VERSION, ICON_PATH


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
        self.token = await super().register_plugin(name=self.plugin_name, developer=self.plugin_infos['Developer'], version=VERSION, icon=ICON_PATH)
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
                "Group": parameter_name.split('_')[1],
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



