import os
import numpy as np
import json
import errno
import math


def read_json(path_json):
    with open(path_json, "r") as load_f:
        my_json = json.load(load_f)
    return my_json


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_label(label):
    h = float(label["3d_dimensions"]["h"])
    w = float(label["3d_dimensions"]["w"])
    length = float(label["3d_dimensions"]["l"])
    x = float(label["3d_location"]["x"])
    y = float(label["3d_location"]["y"])
    z = float(label["3d_location"]["z"])
    rotation_y = float(label["rotation"])
    return h, w, length, x, y, z, rotation_y


def set_label(label, h, w, length, x, y, z, alpha, rotation_y):
    label["3d_dimensions"]["h"] = h
    label["3d_dimensions"]["w"] = w
    label["3d_dimensions"]["l"] = length
    label["3d_location"]["x"] = x
    label["3d_location"]["y"] = y
    label["3d_location"]["z"] = z
    label["alpha"] = alpha
    label["rotation_y"] = rotation_y


def normalize_angle(angle):
    # make angle in range [-0.5pi, 1.5pi]
    alpha_tan = np.tan(angle)
    alpha_arctan = np.arctan(alpha_tan)
    if np.cos(angle) < 0:
        alpha_arctan = alpha_arctan + math.pi
    return alpha_arctan


def get_camera_3d_8points(obj_size, yaw_lidar, center_lidar, center_in_cam, r_velo2cam, t_velo2cam):
    liadr_r = np.matrix(
        [[math.cos(yaw_lidar), -math.sin(yaw_lidar), 0], [math.sin(yaw_lidar), math.cos(yaw_lidar), 0], [0, 0, 1]]
    )
    l, w, h = obj_size
    corners_3d_lidar = np.matrix(
        [
            [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2],
            [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2],
            [0, 0, 0, 0, h, h, h, h],
        ]
    )
    corners_3d_lidar = liadr_r * corners_3d_lidar + np.matrix(center_lidar).T
    corners_3d_cam = r_velo2cam * corners_3d_lidar + t_velo2cam

    x0, z0 = corners_3d_cam[0, 0], corners_3d_cam[2, 0]
    x3, z3 = corners_3d_cam[0, 3], corners_3d_cam[2, 3]
    dx, dz = x0 - x3, z0 - z3
    yaw = math.atan2(-dz, dx)

    alpha = yaw - math.atan2(center_in_cam[0], center_in_cam[2])

    # add transfer
    if alpha > math.pi:
        alpha = alpha - 2.0 * math.pi
    if alpha <= (-1 * math.pi):
        alpha = alpha + 2.0 * math.pi

    alpha_arctan = normalize_angle(alpha)

    return alpha_arctan, yaw


def convert_point(point, matrix):
    return matrix @ point


def get_lidar2cam(calib):
    r_velo2cam = np.array(calib["rotation"])
    t_velo2cam = np.array(calib["translation"])
    r_velo2cam = r_velo2cam.reshape(3, 3)
    t_velo2cam = t_velo2cam.reshape(3, 1)
    return r_velo2cam, t_velo2cam


def gen_lidar2cam(source_root, target_root, label_type="lidar"):
    path_data_info = os.path.join(source_root, "data_info.json")
    data_info = read_json(path_data_info)
    write_path = os.path.join(target_root, "label", label_type)
    mkdir_p(write_path)

    for data in data_info:
        if "calib_virtuallidar_to_camera_path" in data.keys():
            calib_lidar2cam_path = data["calib_virtuallidar_to_camera_path"]
        else:
            calib_lidar2cam_path = data["calib_lidar_to_camera_path"]
        calib_lidar2cam = read_json(os.path.join(source_root, calib_lidar2cam_path))
        r_velo2cam, t_velo2cam = get_lidar2cam(calib_lidar2cam)
        Tr_velo_to_cam = np.hstack((r_velo2cam, t_velo2cam))

        labels_path = data["label_" + label_type + "_std_path"]
        labels = read_json(os.path.join(source_root, labels_path))
        for label in labels:
            h, w, l, x, y, z, yaw_lidar = get_label(label)
            z = z - h / 2
            bottom_center = [x, y, z]
            obj_size = [l, w, h]

            bottom_center_in_cam = r_velo2cam * np.matrix(bottom_center).T + t_velo2cam
            alpha, yaw = get_camera_3d_8points(
                obj_size, yaw_lidar, bottom_center, bottom_center_in_cam, r_velo2cam, t_velo2cam
            )
            cam_x, cam_y, cam_z = convert_point(np.array([x, y, z, 1]).T, Tr_velo_to_cam)

            set_label(label, h, w, l, cam_x, cam_y, cam_z, alpha, yaw)

        labels_path = labels_path.replace("virtuallidar", "lidar")
        write_path = os.path.join(target_root, labels_path)

        with open(write_path, "w") as f:
            json.dump(labels, f)
