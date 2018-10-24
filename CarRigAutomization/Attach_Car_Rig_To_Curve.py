import os
from shutil import copyfile
from Utility.Logging_Extension import logger
from Utility.Config import Config
import bpy
from BlenderUtility.Ops_Functions import configure_scene_for_basic_ops
from BlenderUtility.Import_Export_Functions import high_level_object_import_from_other_blend_file
from CarRigAutomization.Car_Rig_to_Curve import configure_car_rig_for_path_and_ground


def get_car_rig_names(car_rig_prefix=None, car_rig_suffix=None):
    """
    DOES NOT CONSIDER CarRig IK Objects
    :param car_rig_prefix:
    :return:
    """

    # XOR usage of car_rig_prefix and car_rig_suffix
    assert (car_rig_prefix is not None) != (car_rig_suffix is not None)

    car_rig_names = []
    meshes = [object for object in bpy.context.scene.objects if object.type == 'ARMATURE']
    for mesh in meshes:
        if car_rig_prefix is not None:
            if mesh.name.startswith(car_rig_prefix):
                car_rig_names.append(mesh.name)
        else:
            if mesh.name.endswith(car_rig_suffix):
                car_rig_names.append(mesh.name)
    assert len(car_rig_names) > 0

    # Check name for car rigs
    for car_rig_name in car_rig_names:
        if car_rig_name == car_rig_suffix:
            logger.error('car_rig_name: ' + car_rig_name + '. Rig has incorrect name. Expected name: <CarRigName>CarRig')
            assert False    # Expected name: <CarRigName>CarRig'

    return car_rig_names


if __name__:

    parent_dp = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    use_car_rig_config_fp = os.path.join(parent_dp, 'configs/attach_car_rig_to_curve.cfg')

    use_car_rig_config = Config(path_to_config_file=use_car_rig_config_fp)
    path_object_name = use_car_rig_config.get_option_value('path_object_name', str)
    ground_object_name = use_car_rig_config.get_option_value('ground_object_name', str)

    rigged_vehicle_blend_file_path = use_car_rig_config.get_option_value(
        'rigged_vehicle_blend_file_path', target_type=str)

    high_level_object_import_from_other_blend_file(
        blend_file=rigged_vehicle_blend_file_path,
        folder_name='Group',
        target_name='CarRig')

    # ======== IMPORTANT TO AVOID POLL ERRORS ========
    configure_scene_for_basic_ops()
    # ======== ======== ======== ======== ========

    start_frame_number = 1
    end_frame_number = 50

    car_rig_suffix = 'CarRig'
    car_rig_ik_suffix = 'CarRigIK'
    car_rig_suspension_sim_suffix = 'CarRigSuspensionSim'
    car_rig_ground_detect_suffix = 'CarRigGroundDetect'
    car_model_tire_suffix = 'Tire.BL'

    car_rig_obj_names = get_car_rig_names(car_rig_suffix=car_rig_suffix)
    assert len(car_rig_obj_names) == 1
    car_rig_obj_name = car_rig_obj_names[0]
    car_rig_stem = car_rig_obj_name.split(car_rig_suffix, 1)[0]
    car_rig_ik_obj_name = car_rig_stem + car_rig_ik_suffix
    suspension_sim_obj_name = car_rig_stem + car_rig_suspension_sim_suffix
    ground_detect_obj_name = car_rig_stem + car_rig_ground_detect_suffix
    some_tire_obj_name = car_rig_stem + car_model_tire_suffix

    configure_car_rig_for_path_and_ground(
        path_object_name=path_object_name,
        ground_object_name=ground_object_name,
        start_frame_number=start_frame_number,
        end_frame_number=end_frame_number,
        car_rig_object_name=car_rig_obj_name,
        car_rig_ik_object_name=car_rig_ik_obj_name,
        suspension_sim_obj_name=suspension_sim_obj_name,
        ground_detect_object_name=ground_detect_obj_name,
        some_tire_object_name=some_tire_obj_name)


