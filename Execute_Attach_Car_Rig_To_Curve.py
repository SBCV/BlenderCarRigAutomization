import os
from shutil import copyfile

from Utility.Config import Config
from BlenderUtility.Blender_Script_Executor import execute_blender_script

path_to_scripts = os.path.dirname(os.path.realpath(__file__))
path_to_render_trajectory = os.path.join(path_to_scripts, 'CarRigAutomization', 'Attach_Car_Rig_To_Curve.py')

attach_car_rig_to_curve_config_ifp = os.path.join(
    path_to_scripts, 'configs/attach_car_rig_to_curve.cfg')
attach_car_rig_to_curve_config_example_ifp = os.path.join(
    path_to_scripts, 'configs/attach_car_rig_to_curve_example.cfg')

if not os.path.isfile(attach_car_rig_to_curve_config_ifp):
    copyfile(attach_car_rig_to_curve_config_example_ifp, attach_car_rig_to_curve_config_ifp)

car_rig_config = Config(path_to_config_file=attach_car_rig_to_curve_config_ifp)
environment_blend_ifp = car_rig_config.get_option_value('environment_blend_ifp', str)

execute_blender_script(
    path_to_render_trajectory,
    background_mode=False,
    path_to_blend_file=environment_blend_ifp,
    debug_output=False)