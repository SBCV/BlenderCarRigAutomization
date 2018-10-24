import bpy
from Utility.Logging_Extension import logger
from BlenderUtility.Keyframe_Functions import set_scene_keyframe_number
from BlenderUtility.Armature_Functions import add_or_overwrite_bone_constraint_follow_path
from BlenderUtility.Armature_Functions import mute_bone_constraint
from BlenderUtility.Animation_Functions import set_animation_extrapolation
from BlenderUtility.Animation_Functions import clear_animation_data
from BlenderUtility.Keyframe_Functions import add_bone_constraint_keyframe


def configure_car_rig_for_path_and_ground(path_object_name,
                                          ground_object_name,
                                          start_frame_number,
                                          end_frame_number,
                                          car_rig_object_name,
                                          car_rig_ik_object_name,
                                          suspension_sim_obj_name,
                                          ground_detect_object_name,
                                          some_tire_object_name):

    logger.info('configure_car_rig_for_path_and_ground: ...')
    logger.vinfo('ground_object_name', ground_object_name)
    logger.vinfo('start_frame_number', start_frame_number)
    logger.vinfo('end_frame_number', end_frame_number)
    logger.vinfo('car_rig_object_name', car_rig_object_name)
    logger.vinfo('car_rig_ik_object_name', car_rig_ik_object_name)
    logger.vinfo('ground_detect_object_name', ground_detect_object_name)
    logger.vinfo('some_tire_object_name', some_tire_object_name)

    main_control_bone_name = 'MainControl'

    set_rig_ground_detect(ground_detect_object_name, ground_object_name)

    # set_path_ground_target(path_object_name, ground_object_name)
    # Important: Compute the path length after applying the modifier
    path_length = compute_path_length(path_object_name)

    set_path_length(car_rig_name=car_rig_object_name, length=path_length)

    tire_diameter = bpy.data.objects[some_tire_object_name].dimensions[1]
    set_tire_diameter(car_rig_name=car_rig_object_name, tire_diameter=tire_diameter)

    add_or_overwrite_bone_constraint_follow_path(armature_object_name=car_rig_ik_object_name,
                                                 bone_name=main_control_bone_name,
                                                 constraint_name='Follow Path',
                                                 target_curve_name=path_object_name,
                                                 use_curve_follow=True,  # default car rig addon value
                                                 use_fixed_location=True,  # default car rig addon value
                                                 forward_axis='TRACK_NEGATIVE_Y'
                                                 )

    set_scene_keyframe_number(start_frame_number=start_frame_number, end_frame_number=end_frame_number)

    # clear the animation data to get rid of previous inserted keyframes
    clear_animation_data(car_rig_ik_object_name)

    add_car_keyframes(rig_ik_object_name=car_rig_ik_object_name,
                      start_frame_number=start_frame_number,
                      end_frame_number=end_frame_number)

    set_animation_extrapolation(car_rig_ik_object_name, fcurve_extrapolation_type='LINEAR')

    # Make sure tail constraint is enabled
    mute_bone_constraint(armature_object_name=car_rig_ik_object_name,
                         bone_name='IK',
                         constraint_name='IK',
                         mute=False)

    # Make some objects invisible during rendering
    bpy.data.objects[suspension_sim_obj_name].hide_render = True
    bpy.data.objects[suspension_sim_obj_name].hide = True               # To reflect hide_render in the 3D view
    bpy.data.objects[ground_detect_object_name].hide_render = True
    bpy.data.objects[ground_detect_object_name].hide = True             # To reflect hide_render in the 3D view

    logger.info('configure_car_rig_for_path_and_ground: Done')


def set_path_ground_target_and_get_length(path_object_name, ground_name):

    bpy.data.objects[path_object_name].modifiers['Shrinkwrap'].target = bpy.data.objects[ground_name]
    # Important: Compute the path length after applying the modifier
    length = compute_path_length(path_object_name)
    # set_mode(path_object_name, 'OBJECT')
    return length


def set_path_ground_target(path_object_name, ground_name):
    bpy.data.objects[path_object_name].modifiers['Shrinkwrap'].target = bpy.data.objects[ground_name]


def set_rig_ground_detect(ground_detect_name, ground_name, ground_detect_distance=0):
    logger.info('set_rig_ground: ...')
    bpy.data.objects[ground_detect_name].modifiers['Shrinkwrap'].target = bpy.data.objects[ground_name]
    bpy.data.objects[ground_detect_name].modifiers['Shrinkwrap'].offset = ground_detect_distance
    logger.info('set_rig_ground: Done')


def set_path_length(car_rig_name, length):
    logger.info('set_path_length: ...')
    bpy.data.objects[car_rig_name]["Path Length"] = length
    logger.info('set_path_length: Done')


def set_tire_diameter(car_rig_name, tire_diameter):
    logger.info('set_wheel_size_and_path_length: ...')

    # we asume that all wheels of the car have the same diameter
    # "wheel diameter front" is a custom property of the object
    bpy.data.objects[car_rig_name]["Wheel Diameter Front"] = tire_diameter
    bpy.data.objects[car_rig_name]["Wheel Diameter Back"] = tire_diameter

    logger.info('set_wheel_size_and_path_length: Done')


def compute_path_length(path_object_name):
    logger.info('addon_compute_path_length: ...')

    bpy.ops.object.select_all(action='DESELECT')
    ob = bpy.data.objects[path_object_name]
    bpy.context.scene.objects.active = ob
    ob.select = True
    path_length = -1
    if ob and ob.select and ob.type == 'CURVE':
        em = (ob.mode == 'EDIT')
        bpy.ops.object.duplicate_move()
        bpy.ops.object.mode_set()
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.convert(target='MESH', keep_original=False)

        # now the active object is the one created by bpy.ops.object.duplicate_move()
        logger.info('Duplicate_move_object: ' + bpy.context.active_object.name)
        ve = bpy.context.active_object.data.vertices
        path_length = 0
        for i in bpy.context.active_object.data.edges:
            distance = ve[i.vertices[0]].co - ve[i.vertices[1]].co
            path_length += distance.length
        path_length = round(path_length, 4)
        bpy.ops.object.delete()

        if em: bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    logger.info('path_length: ' + str(path_length))
    logger.info('addon_compute_path_length: ...')
    return path_length


def add_car_keyframes(rig_ik_object_name, start_frame_number, end_frame_number):

    """

    :return:
    """
    logger.info('add_keyframe: ...')

    bone_main_control_name = 'MainControl'
    constraint_follow_path_name = 'Follow Path'
    attribute_offset_factor_name = 'offset_factor'

    bone_IK_name = 'IK'
    constraint_IK_name = 'IK'
    attribute_influence_name = 'influence'

    # constraint is in BMWCarRigIK / Pose / MainControl
    keyframe_object = bpy.data.objects[rig_ik_object_name]
    bpy.context.scene.objects.active = keyframe_object
    keyframe_object.select = True

    bpy.ops.object.mode_set(mode='POSE')

    # Configure the animation of the main bone (so the car actually moves)

    # ====== Note ======
    # Right click on "Copy Data Path" in order to "Copy the RNA datapath for this property"
    # e.g. pose.bones["MainControl"].constraints["Follow Path"].offset_factor
    # =================

    frac = 1.0 / float(end_frame_number - start_frame_number)

    # Set the influence of the ik bone / constraint on frame 1 to 0
    # Without resetting a repitition of the animation will result in strange motion
    add_bone_constraint_keyframe(object_name=rig_ik_object_name,
                                 bone_name=bone_main_control_name,
                                 constraint_name=constraint_follow_path_name,
                                 frame_number=start_frame_number+1,
                                 constraint_attribute_name=attribute_offset_factor_name,
                                 constraint_attribute_value=frac)

    add_bone_constraint_keyframe(object_name=rig_ik_object_name,
                                 bone_name=bone_main_control_name,
                                 constraint_name=constraint_follow_path_name,
                                 frame_number=end_frame_number-1,
                                 constraint_attribute_name=attribute_offset_factor_name,
                                 constraint_attribute_value=1 - frac)

    # Configure the animation of the IK bone (used to naturally move along the path)

    # Set the influence of the ik bone / constraint on frame 1 to 0
    # Without resetting a repitition of the animation will result in strange motion
    add_bone_constraint_keyframe(object_name=rig_ik_object_name,
                                 bone_name=bone_IK_name,
                                 constraint_name=constraint_IK_name,
                                 frame_number=1,
                                 constraint_attribute_name=attribute_influence_name,
                                 constraint_attribute_value=0)

    # Enable the influence on frame 1
    add_bone_constraint_keyframe(object_name=rig_ik_object_name,
                                 bone_name=bone_IK_name,
                                 constraint_name=constraint_IK_name,
                                 frame_number=2,
                                 constraint_attribute_name=attribute_influence_name,
                                 constraint_attribute_value=1)

    # Make sure to to start the animation from scratch (do not use pose information from previous runs)
    bpy.context.scene.frame_current = 0

    logger.info('add_keyframe: Done')
