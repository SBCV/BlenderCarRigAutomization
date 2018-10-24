import bpy
from mathutils import Matrix, Vector

from math import degrees
from Utility.Logging_Extension import logger

from BlenderUtility.Armature_Functions import clear_and_set_inverse_bone_constraint_child_of, mute_bone_constraint
from BlenderUtility.Armature_Functions import snap_bones_to_cursor, set_pose_position
from BlenderUtility.Group_Functions import move_group_to_layer

from BlenderUtility.Object_Functions import clear_and_set_inverse_object_constraint_child_of, \
    show_viewport_object_modifier
from BlenderUtility.Object_Functions import set_cursor_to_objects, set_object_parent_bone
from BlenderUtility.Ops_Functions import configure_scene_for_basic_ops
from BlenderUtility.Ops_Functions import set_mode

eps = 0.0001


def check_wheel_origins(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name):
    assert bpy.data.objects[tire_fl_name].location.length > eps
    assert bpy.data.objects[tire_fr_name].location.length > eps
    assert bpy.data.objects[tire_bl_name].location.length > eps
    assert bpy.data.objects[tire_br_name].location.length > eps


def recenter_objects_if_necessary(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name):
    logger.info('recenter_objects_if_necessary: ...')

    front_axle_center = compute_xy_axle_center(tire_fl_name, tire_fr_name)
    logger.vinfo('front_axle_center', front_axle_center)
    front_axle_center_xy0 = front_axle_center.xyz
    front_axle_center_xy0.z = 0

    back_axle_center = compute_xy_axle_center(tire_bl_name, tire_br_name)
    logger.vinfo('back_axle_center', back_axle_center)
    back_axle_center_xy0 = back_axle_center.xyz
    back_axle_center_xy0.z = 0

    axle_diff = front_axle_center_xy0 - back_axle_center_xy0

    y_is_dir_axis = abs(axle_diff.x) < eps
    x_is_dir_axis = abs(axle_diff.y) < eps

    if not (y_is_dir_axis is not x_is_dir_axis):
        logger.vinfo('y_is_dir_axis', y_is_dir_axis)
        logger.vinfo('x_is_dir_axis', x_is_dir_axis)
        assert False

    if y_is_dir_axis:
        if abs(front_axle_center.x) > eps:
            for obj in bpy.data.objects:
                obj.location.x -= front_axle_center.x
    elif x_is_dir_axis:
        if (front_axle_center.y) > eps:
            for obj in bpy.data.objects:
                obj.location.y -= front_axle_center.y
    else:
        assert False
    logger.info('recenter_objects_if_necessary: Done')


def compute_xy_axle_center(tire_l_name, tire_r_name, check_axle=False):
    logger.info('compute_xy_axle_center: ...')

    l_center = bpy.data.objects[tire_l_name].location
    r_center = bpy.data.objects[tire_r_name].location
    axle_center = l_center + 0.5 * (r_center - l_center)

    if check_axle:
        check_axle_center(
            axle_center, tire_l_name, tire_r_name, r_center, l_center)

    logger.vinfo('tire_l_name', tire_l_name)
    logger.vinfo('tire_r_name', tire_r_name)
    logger.vinfo('l_center', l_center)
    logger.vinfo('r_center', r_center)

    logger.info('compute_xy_axle_center: Done')
    return axle_center


def check_axle_center(axle_center, tire_l_name, tire_r_name, fr_center, fl_center):
    # Assumption that the car is aligned to one of the main axis
    if not (abs(axle_center.x) < 0.0001 or abs(axle_center.y) < 0.0001):  # could be something like -0.00000
        logger.vinfo('tire_l_name', tire_l_name)
        logger.vinfo('tire_r_name', tire_r_name)
        logger.vinfo('fr_center', fr_center)
        logger.vinfo('fl_center', fl_center)
        logger.vinfo('axle_center', axle_center)
        logger.vinfo('axle_center.x', "%.10f" % axle_center.x)
        logger.vinfo('axle_center.y', "%.10f" % axle_center.y)
        assert False  # Front L and R are NOT symmetric


def prepare_model_for_rigging(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name, check_axle=True):
    """
    This method automates the following steps

    Add an empty between the front wheels
      Select both front wheels (shift select)
      Shift + s / Cursor to selected
      Shift + A / Empty

    Parent everything to the empty
      Select everything, select the empty, ctrl + p / Object

    Clear the location of the empty
      Select the empty, alt + g

    Move the empty, so the wheels touch the x-y plane

    Clear parents
      Select everything, alt + p / clear and keep transformation

    Delete the empty

    Apply rotation and scale
      select everything, ctlr + a / Rotation & Scale


    """

    # for obj in bpy.data.objects:
    #     logger.vinfo('obj.name', obj.name)

    check_wheel_origins(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name)

    recenter_objects_if_necessary(tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name)

    front_axle_center = compute_xy_axle_center(
        tire_fl_name, tire_fr_name, check_axle=check_axle)
    front_axle_center_xy0 = front_axle_center.xyz
    front_axle_center_xy0.z = 0

    back_axle_center = compute_xy_axle_center(tire_bl_name, tire_br_name, check_axle=check_axle)
    back_axle_center_xy0 = back_axle_center.xyz
    back_axle_center_xy0.z = 0

    car_dir_vec = front_axle_center_xy0 - back_axle_center_xy0

    # The car will look along the negative y axis (in blenders front view, the front side of the car is visible)
    future_alignment_axis = Vector((0, -1, 0))

    angle_between_rad = -car_dir_vec.angle(future_alignment_axis)
    angle_between_degrees = degrees(angle_between_rad)
    logger.vinfo('front_axle_center_xy0', front_axle_center_xy0)
    logger.vinfo('future_alignment_axis', future_alignment_axis)
    logger.vinfo('angle_between_degrees', angle_between_degrees)

    rot_mat = Matrix.Rotation(angle_between_rad, 4, 'Z')

    # rotate all objects
    for obj in bpy.data.objects:
        obj.matrix_world = rot_mat * obj.matrix_world

    rotated_front_axle_center_xy = rot_mat * front_axle_center_xy0

    # translate all objects
    # assert rotated_front_axle_center_xy.x == 0 or rotated_front_axle_center_xy.y == 0
    some_tire = bpy.data.objects[tire_fl_name]
    tire_height = some_tire.dimensions[2] / some_tire.scale[2]
    trans_vec = Vector((rotated_front_axle_center_xy.x,
                        rotated_front_axle_center_xy.y,
                        front_axle_center.z - tire_height / 2.0))

    logger.vinfo('front_axle_center.z', front_axle_center.z)
    logger.vinfo('tire_height/ 2.0', tire_height/ 2.0)
    logger.vinfo('trans_vec', trans_vec)

    for obj in bpy.data.objects:
        obj.location -= trans_vec

    # Apply rotation and scale
    for obj in bpy.data.objects:
        set_mode(active_object_name=obj.name,
                 mode='OBJECT',
                 configure_scene_for_basic_ops=False)
        bpy.ops.object.transform_apply(rotation=True, scale=True)


def apply_rig_to_model(car_rig_prefix,
                       car_body_group_name,
                       car_wheels_group_name,
                       tire_fl_name,
                       tire_fr_name,
                       tire_bl_name,
                       tire_br_name):
    logger.info('bpy.context.scene.active_layer:' + str(bpy.context.scene.active_layer))
    rig_layer_id = bpy.context.scene.active_layer

    # ======== IMPORTANT TO AVOID POLL ERRORS ========
    configure_scene_for_basic_ops()
    # ======== ======== ======== ======== ========

    logger.info('Adjust Rig to Car Model')

    car_rig_name = 'CarRig'
    car_rig_ground_detect_name = 'CarRigGroundDetect'
    car_rig_ik_name = 'CarRigIK'
    car_rig_suspension_sim_name = 'CarRigSuspensionSim'

    # CarRig Armature with Bones (parent/child/sibling) structure:
    #   MASTER
    #       car.roll
    #           axle.fl
    #               steer.fl
    #                   wheel.fl
    #           axle.fr
    #           axle.bl
    #           axle.br

    set_cursor_to_objects(object_names=[tire_fl_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['steer.fl', 'wheel.fl', 'hub.fl'])

    set_cursor_to_objects(object_names=[tire_fr_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['steer.fr', 'wheel.fr', 'hub.fr'])

    set_cursor_to_objects(object_names=[tire_bl_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['rotation.bl', 'wheel.bl', 'hub.bl'])

    set_cursor_to_objects(object_names=[tire_br_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['rotation.br', 'wheel.br', 'hub.br'])

    # for vert in bpy.data.objects['CarRigGroundDetect'].data.vertices:
    #     #logger.info(str(vert.co.x) + ' ' + str(vert.co.y) + ' ' + str(vert.co.z))
    #     logger.info(vert.co)

    # Pos x = Left side, Neg X = Right side
    # Neg y = Front side, Pos y = Back side

    ground_detect_obj_loc = bpy.data.objects[car_rig_ground_detect_name].location

    # Right Side, Back
    br_vert = bpy.data.objects[car_rig_ground_detect_name].data.vertices[0]
    br_vert.co.xy = bpy.data.objects[tire_br_name].location.xy - ground_detect_obj_loc.xy
    # Left Side, Front
    fl_vert = bpy.data.objects[car_rig_ground_detect_name].data.vertices[1]
    fl_vert.co.xy = bpy.data.objects[tire_fl_name].location.xy - ground_detect_obj_loc.xy
    # Right Side, Front
    fr_vert = bpy.data.objects[car_rig_ground_detect_name].data.vertices[2]
    fr_vert.co.xy = bpy.data.objects[tire_fr_name].location.xy - ground_detect_obj_loc.xy
    # Left Side, Back
    bl_vert = bpy.data.objects[car_rig_ground_detect_name].data.vertices[3]
    bl_vert.co.xy = bpy.data.objects[tire_bl_name].location.xy - ground_detect_obj_loc.xy

    # Configure the front and back axles
    set_cursor_to_objects(object_names=[tire_bl_name, tire_br_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['rear.rotation', 'axle.bl', 'axle.br'])

    set_cursor_to_objects(object_names=[tire_fl_name, tire_fr_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['front.rotation', 'steer.pointer', 'axle.fl', 'axle.fr'])

    set_cursor_to_objects(object_names=[tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name])
    snap_bones_to_cursor(
        armature_object_name=car_rig_name,
        bone_names_list=['MASTER', 'car.roll'])

    # CarRig Armature with Bones (parent/child/sibling) structure:
    #   MainControl
    #   IK
    #       DriftControl
    #       IKTarget

    # # Configure the RigIK
    set_cursor_to_objects(object_names=[tire_bl_name, tire_br_name])
    bpy.context.scene.cursor_location.z = 0
    snap_bones_to_cursor(
        armature_object_name=car_rig_ik_name,
        bone_names_list=['IKTarget'])

    # Configure the CarRIgSuspensionSim
    # The last vertex (index 8) in the CarRIgSuspensionSim mesh is the median of the mesh
    set_cursor_to_objects(object_names=[tire_fl_name, tire_fr_name, tire_bl_name, tire_br_name])
    y_diff = bpy.data.objects[car_rig_suspension_sim_name].data.vertices[
                 8].co.y - bpy.context.scene.cursor_location.y
    for vert in bpy.data.objects[car_rig_suspension_sim_name].data.vertices:
        vert.co.y -= y_diff

    move_group_to_layer(group_name=car_body_group_name, layer_id=rig_layer_id)
    car_body_obj_name = bpy.data.groups[car_body_group_name].objects[0].name
    if not car_body_obj_name.endswith('Body'):
        logger.vinfo('car_body_group_name', car_body_group_name)
        logger.vinfo('car_body_obj_name', car_body_obj_name)
        assert False  # car_body_obj_name is incorrect (does not end with Body)

    for ob in bpy.data.groups[car_body_group_name].objects:
        set_object_parent_bone(
            child_object_name=ob.name,
            armature_object_name=car_rig_name,
            bone_name='car.roll')

    # Hide objects
    # bpy.data.objects['CarRigGround'].hide = True
    # bpy.data.objects[car_rig_ik_name].hide = True
    # bpy.data.objects[car_rig_suspension_sim_name].hide = True


    move_group_to_layer(
        group_name=car_wheels_group_name,
        layer_id=rig_layer_id)
    set_object_parent_bone(
        child_object_name=tire_fl_name,
        armature_object_name=car_rig_name,
        bone_name='wheel.fl')
    set_object_parent_bone(
        child_object_name=tire_fr_name,
        armature_object_name=car_rig_name,
        bone_name='wheel.fr')
    set_object_parent_bone(
        child_object_name=tire_bl_name,
        armature_object_name=car_rig_name,
        bone_name='wheel.bl')
    set_object_parent_bone(
        child_object_name=tire_br_name,
        armature_object_name=car_rig_name,
        bone_name='wheel.br')

    # Reset child_of constraints of bones
    # IMPORTANT: THERE WILL BE NO EFFECT WITHOUT POSE POSITION == 'POSE'
    set_pose_position(armature_object_name=car_rig_name, pose_position='POSE')

    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='hub.fl',
        constraint_name='Child Of')
    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='hub.fr',
        constraint_name='Child Of')
    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='hub.bl',
        constraint_name='Child Of')
    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='hub.br',
        constraint_name='Child Of')

    # IMPORTANT: DO NOT SET THE POSE POSITION BACK TO 'REST'

    # Reset child_of constraints of suspension sim
    bpy.data.objects[car_rig_suspension_sim_name].constraints['Child Of'].mute = False
    clear_and_set_inverse_object_constraint_child_of(
        object_name=car_rig_suspension_sim_name,
        constraint_name='Child Of')

    # Reset child_of constraints of MASTER bone
    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='MASTER',
        constraint_name='Child Of')

    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_name,
        bone_name='MASTER',
        constraint_name='Child Of.001')

    clear_and_set_inverse_bone_constraint_child_of(
        armature_object_name=car_rig_ik_name,
        bone_name='IK',
        constraint_name='Child Of')

    mute_bone_constraint(
        armature_object_name=car_rig_ik_name,
        bone_name='MainControl',
        constraint_name='Follow Path',
        mute=False)

    show_viewport_object_modifier(
        object_name=car_rig_ground_detect_name,
        modifier_name='Shrinkwrap',
        show_viewport=True)

    # Adjust the rig names
    bpy.data.objects[car_rig_name].name = car_rig_prefix + car_rig_name
    bpy.data.objects[car_rig_ik_name].name = car_rig_prefix + car_rig_ik_name
    bpy.data.objects[car_rig_suspension_sim_name].name = car_rig_prefix + car_rig_suspension_sim_name
    bpy.data.objects[car_rig_ground_detect_name].name = car_rig_prefix + car_rig_ground_detect_name

    # Adjust scale of car body
    for child in bpy.data.groups[car_body_group_name].objects:
        set_mode(active_object_name=child.name,
                 mode='OBJECT',
                 configure_scene_for_basic_ops=False)
        bpy.ops.object.transform_apply(scale=True)

        obj = bpy.data.objects[child.name]

    # THIS IS IMPORTANT (Otherwise the body and the wheels are not loaded while importing the rig)
    car_rig_group = bpy.data.groups.get(car_rig_name)
    for child in bpy.data.groups[car_body_group_name].objects:
        obj = bpy.data.objects[child.name]
        car_rig_group.objects.link(obj)

    for child in bpy.data.groups[car_wheels_group_name].objects:
        obj = bpy.data.objects[child.name]
        car_rig_group.objects.link(obj)
