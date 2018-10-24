import os

from BlenderUtility.Blender_Script_Executor import execute_blender_script
from CarRigAutomization.Attach_Rig_to_Car_Model import vehicle_blend_ifp

path_to_scripts = os.path.dirname(os.path.realpath(__file__))
path_to_render_trajectory = os.path.join(path_to_scripts, 'CarRigAutomization', 'Attach_Rig_to_Car_Model.py')

execute_blender_script(path_to_render_trajectory,
                       background_mode=False,
                       path_to_blend_file=vehicle_blend_ifp,
                       debug_output=False)