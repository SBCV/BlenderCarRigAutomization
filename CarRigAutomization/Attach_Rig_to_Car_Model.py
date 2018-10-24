import os
from shutil import copyfile

from Utility.Config import Config
from Utility.Logging_Extension import logger


path_rigging_scripts = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

attach_rig_to_car_model_config_ifp = os.path.join(
    path_rigging_scripts, 'configs/attach_rig_to_car_model.cfg')
attach_rig_to_car_model_example_config_ifp = os.path.join(
    path_rigging_scripts, 'configs/attach_rig_to_car_model_example.cfg')

if not os.path.isfile(attach_rig_to_car_model_config_ifp):
    copyfile(attach_rig_to_car_model_example_config_ifp, attach_rig_to_car_model_config_ifp)

attach_rig_to_car_model_config = Config(
    path_to_config_file=attach_rig_to_car_model_config_ifp)

vehicle_blend_ifp = attach_rig_to_car_model_config.get_option_value(
    'vehicle_blend_ifp', target_type=str)
vehicle_config_ifp = attach_rig_to_car_model_config.get_option_value(
    'vehicle_config_ifp', target_type=str)
car_rig_prefix = attach_rig_to_car_model_config.get_option_value(
    'car_rig_prefix', target_type=str)
rig_blend_ifp = attach_rig_to_car_model_config.get_option_value(
    'rig_blend_ifp', target_type=str)

check_axle = attach_rig_to_car_model_config.get_option_value('check_axle', target_type=bool)

if not os.path.isfile(vehicle_blend_ifp):
    logger.vinfo('vehicle_blend_ifp', vehicle_blend_ifp)
    assert False
if not os.path.isfile(vehicle_config_ifp):
    logger.vinfo('path_to_vehicle_config_file', vehicle_config_ifp)
    assert False

rigged_car_blend_ofp = attach_rig_to_car_model_config.get_option_value(
    'rigged_car_blend_ofp', target_type=str)


def log_tire_names(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name):
    logger.info('tire_fl_name: ' + tire_fl_name)
    logger.info('tire_fr_name: ' + tire_fr_name)
    logger.info('tire_bl_name: ' + tire_bl_name)
    logger.info('tire_br_name: ' + tire_br_name)


if __name__ == '__main__':

    # =============== PREQUISITES BEFORE RUNNING THIS SCRIPT ===============

    # The vehicle must be PLACED CORRECTLY
    #   NOT ZERO CENTERED
    #   Otherwise this may BREAK THE RIG (Bones are getting deleted)
    #   Use a cube to adjust the size of the object

    # SCALE the vehicle to the CORRECT extend

    # Make a SINGLE MESH for EACH WHEEL
    #   strg + j

    # Add all body parts to a group (strg + g)
    # Add all wheel parts to a group (strg + g)

    # RECENTER the wheels if necessary (i.e. they must rotate smoothly around the car axis)
    #   Select object
    #   Go into edit mode
    #   Select all vertices
    #   shift + s / cursor to selected
    #   Go into object mode
    #   ctrl + alt +shift + c / Origin to 3D Cursor

    # ======================================================================

    import bpy
    from BlenderUtility.Import_Export_Functions import high_level_object_import_from_other_blend_file
    from BlenderUtility.Modifier_Functions import apply_modifiers
    from CarRigAutomization.Rig_to_Car_Model import prepare_model_for_rigging
    from CarRigAutomization.Rig_to_Car_Model import apply_rig_to_model

    vehicle_config = Config(vehicle_config_ifp)

    # ============= Car Model Parameters =============
    car_body_group_name = vehicle_config.get_option_value('car_body_group_name', target_type=str)

    car_wheels_group_name = vehicle_config.get_option_value('car_wheels_group_name', target_type=str)
    logger.vinfo('car_wheels_group_name', car_wheels_group_name)

    # In the original version of the example car model the naming of the wheels is incorrect w.r.t to their position
    # RR=FL, RL=FR, FL=RR, FR==RL
    tire_fl_name = vehicle_config.get_option_value('tire_fl_name', target_type=str)
    tire_fr_name = vehicle_config.get_option_value('tire_fr_name', target_type=str)
    tire_bl_name = vehicle_config.get_option_value('tire_bl_name', target_type=str)
    tire_br_name = vehicle_config.get_option_value('tire_br_name', target_type=str)

    assert tire_fl_name.endswith('Tire.FL')
    assert tire_fr_name.endswith('Tire.FR')
    assert tire_bl_name.endswith('Tire.BL')
    assert tire_br_name.endswith('Tire.BR')

    # ====================================================

    def make_objects_single_user():
        # sel = bpy.context.selected_objects
        for obj in bpy.data.objects:
            mesh = obj.data
            if mesh:
                obj.data = mesh.copy()
            mat = obj.active_material
            if mat:
                obj.active_material = mat.copy()

    log_tire_names(
        tire_fl_name,
        tire_fr_name,
        tire_bl_name,
        tire_br_name)

    # ALL MIRROR MODIFIERS MUST BE APPLIED TO THE CAR MODEL BEFORE ADJUSTING THE CAR RIG
    # ALL SOLIDIFY MODIFIERS MUST BE APPLIED TO THE CAR MODEL BEFORE ADJUSTING THE CAR RIG
    apply_modifiers(['Mirror', 'Solidify'])

    make_objects_single_user()

    prepare_model_for_rigging(
        tire_fl_name,
        tire_fr_name,
        tire_bl_name,
        tire_br_name,
        check_axle=check_axle)

    high_level_object_import_from_other_blend_file(
        blend_file=rig_blend_ifp,
        folder_name='Group',
        target_name='CarRig')

    apply_rig_to_model(
        car_rig_prefix,
        car_body_group_name,
        car_wheels_group_name,
        tire_fl_name,
        tire_fr_name,
        tire_bl_name,
        tire_br_name)

    bpy.ops.wm.save_as_mainfile(filepath=rigged_car_blend_ofp)