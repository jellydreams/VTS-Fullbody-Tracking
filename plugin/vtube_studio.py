from .mediapipe import get_parameters_names

from debug import start_timer, stop_timer


async def connection_vts(vts):
    # Initialize VTube Studio connection
    await vts.connect()

    # Authenticate with VTube Studio API
    # print('authentification VtubeStudio..')
    await vts.request_authenticate_token()  # get token
    await vts.request_authenticate()  # use token

    # TODO: Error Message if Vtube Studio not open
    # TODO: Error Message if Port cant connect


async def create_parameters_vts(vts):
    start_time = start_timer()

    # print('Create parameters in VTube Studio')

    # Prepare parameter names for each body part
    parameter_names = get_parameters_names()

    # Maximum of 100 parameters allowed to be created in VTube Studio per plugin
    for parameter_name in parameter_names:
        # Add custom parameters in VTube Studio
        send_request_new_parameter = vts.vts_request.requestCustomParameter(parameter_name, min=-10, max=10)
        await vts.request(send_request_new_parameter)

    stop_timer(start_time, 'create parameters in vts')


async def send_paramters_vts(vts, values, names):
    """  parameters in VTube Studio """

    send_request_parameter = vts.vts_request.requestSetMultiParameterValue(names, values, weight=1, face_found=True, mode='set')
    await vts.request(send_request_parameter)