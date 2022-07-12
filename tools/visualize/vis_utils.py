#!/usr/bin/env python
# coding: utf-8
import os
import json
import errno
import numpy as np
import cv2
import pickle


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def id_to_str(id, digits=6):
    result = ""
    for i in range(digits):
        result = str(id % 10) + result
        id //= 10
    return result


def load_pkl(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def read_json(path):
    with open(path, "r") as f:
        my_json = json.load(f)
        return my_json


def get_label(label):
    h = float(label[0]["h"])
    w = float(label[0]["w"])
    length = float(label[0]["l"])
    x = float(label[1]["x"])
    y = float(label[1]["y"])
    z = float(label[1]["z"])
    rotation_y = float(label[-1])
    return h, w, length, x, y, z, rotation_y


def get_lidar2cam(calib):
    if "Tr_velo_to_cam" in calib.keys():
        velo2cam = np.array(calib["Tr_velo_to_cam"]).reshape(3, 4)
        r_velo2cam = velo2cam[:, :3]
        t_velo2cam = velo2cam[:, 3].reshape(3, 1)
    else:
        r_velo2cam = np.array(calib["rotation"])
        t_velo2cam = np.array(calib["translation"])
    return r_velo2cam, t_velo2cam


def get_cam_calib_intrinsic(calib_path):
    my_json = read_json(calib_path)
    cam_K = my_json["cam_K"]
    calib = np.zeros([3, 4])
    calib[:3, :3] = np.array(cam_K).reshape([3, 3], order="C")

    return calib


def plot_rect3d_on_img(img, num_rects, rect_corners, color=(0, 255, 0), thickness=1):
    """Plot the boundary lines of 3D rectangular on 2D images.

    Args:
        img (numpy.array): The numpy array of image.
        num_rects (int): Number of 3D rectangulars.
        rect_corners (numpy.array): Coordinates of the corners of 3D
            rectangulars. Should be in the shape of [num_rect, 8, 2].
        color (tuple[int]): The color to draw bboxes. Default: (0, 255, 0).
        thickness (int, optional): The thickness of bboxes. Default: 1.
    """
    line_indices = ((0, 1), (0, 3), (0, 4), (1, 2), (1, 5), (3, 2), (3, 7), (4, 5), (4, 7), (2, 6), (5, 6), (6, 7))
    for i in range(num_rects):
        corners = rect_corners[i].astype(np.int)

        for start, end in line_indices:
            radius = 5
            color = (0, 0, 250)
            thickness = 1
            cv2.circle(img, (corners[start, 0], corners[start, 1]), radius, color, thickness)
            cv2.circle(img, (corners[end, 0], corners[end, 1]), radius, color, thickness)
            color = (0, 255, 0)
            cv2.line(
                img,
                (corners[start, 0], corners[start, 1]),
                (corners[end, 0], corners[end, 1]),
                color,
                thickness,
                cv2.LINE_AA,
            )

    return img.astype(np.uint8)


def get_rgb(img_path):
    return cv2.imread(img_path)


def points_cam2img(points_3d, calib_intrinsic, with_depth=False):
    """Project points from camera coordicates to image coordinates.

    points_3d: N x 8 x 3
    calib_intrinsic: 3 x 4
    return: N x 8 x 2
    """
    points_num = list(points_3d.shape)[:-1]
    points_shape = np.concatenate([points_num, [1]], axis=0)
    points_2d_shape = np.concatenate([points_num, [3]], axis=0)
    # assert len(calib_intrinsic.shape) == 2, 'The dimension of the projection' \
    #                                  f' matrix should be 2 instead of {len(calib_intrinsic.shape)}.'
    # d1, d2 = calib_intrinsic.shape[:2]
    # assert (d1 == 3 and d2 == 3) or (d1 == 3 and d2 == 4) or (
    #         d1 == 4 and d2 == 4), 'The shape of the projection matrix' \
    #                               f' ({d1}*{d2}) is not supported.'
    # if d1 == 3:
    #     calib_intrinsic_expanded = np.eye(4, dtype=calib_intrinsic.dtype)
    #     calib_intrinsic_expanded[:d1, :d2] = calib_intrinsic
    #     calib_intrinsic = calib_intrinsic_expanded

    # previous implementation use new_zeros, new_one yeilds better results

    points_4 = np.concatenate((points_3d, np.ones(points_shape)), axis=-1)
    point_2d = np.matmul(calib_intrinsic, points_4.T.swapaxes(1, 2).reshape(4, -1))
    point_2d = point_2d.T.reshape(points_2d_shape)
    point_2d_res = point_2d[..., :2] / point_2d[..., 2:3]

    if with_depth:
        return np.cat([point_2d_res, point_2d[..., 2:3]], dim=-1)
    return point_2d_res


def compute_corners_3d(dim, rotation_y):
    c, s = np.cos(rotation_y), np.sin(rotation_y)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)
    # R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)
    l, w, h = dim[0], dim[1], dim[2]
    x_corners = [-l / 2, l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2]
    y_corners = [w / 2, w / 2, w / 2, w / 2, -w / 2, -w / 2, -w / 2, -w / 2]
    z_corners = [h, h, 0, 0, h, h, 0, 0]
    corners = np.array([x_corners, y_corners, z_corners], dtype=np.float32)
    corners_3d = np.dot(R, corners).transpose(1, 0)

    return corners_3d


def compute_box_3d(dim, location, rotation_y):
    # dim: 3
    # location: 3
    # rotation_y: 1
    # return: 8 x 3
    corners_3d = compute_corners_3d(dim, rotation_y)
    corners_3d = corners_3d + np.array(location, dtype=np.float32).reshape(1, 3)

    return corners_3d


def get_cam_8_points(labels, calib_lidar2cam_path):
    """Plot the boundaries of 3D BBox with label on 2D image.

        Args:
            label: h, w, l, x, y, z, rotaion
            image_path: Path of image to be visualized
            calib_lidar2cam_path: Extrinsic of lidar2camera
            calib_intrinsic_path: Intrinsic of camera
            save_path: Save path for visualized images

    ..code - block:: none


                         front z
                              /
                             /
               (x0, y0, z1) + -----------  + (x1, y0, z1)
                           /|            / |
                          / |           /  |
            (x0, y0, z0) + ----------- +   + (x1, y1, z1)
                         |  /      .   |  /
                         | / oriign    | /
            (x0, y1, z0) + ----------- + -------> x right
                         |             (x1, y1, z0)
                         |
                         v
                    down y

    """
    calib_lidar2cam = read_json(calib_lidar2cam_path)
    r_velo2cam, t_velo2cam = get_lidar2cam(calib_lidar2cam)
    camera_8_points_list = []
    for label in labels:
        h, w, l, x, y, z, yaw_lidar = get_label(label)
        z = z - h / 2
        bottom_center = [x, y, z]
        obj_size = [l, w, h]
        lidar_8_points = compute_box_3d(obj_size, bottom_center, yaw_lidar)
        # lidar_8_points = np.matrix([[x - l / 2, y + w / 2, z + h],
        #                             [x + l / 2, y + w / 2, z + h],
        #                             [x + l / 2, y + w / 2, z],
        #                             [x - l / 2, y + w / 2, z],
        #                             [x - l / 2, y - w / 2, z + h],
        #                             [x + l / 2, y - w / 2, z + h],
        #                             [x + l / 2, y - w / 2, z],
        #                             [x - l / 2, y - w / 2, z]])
        camera_8_points = r_velo2cam * np.matrix(lidar_8_points).T + t_velo2cam
        camera_8_points_list.append(camera_8_points.T)

    return camera_8_points_list


def vis_label_in_img(camera_8_points_list, img_path, path_camera_intrinsic, save_path):
    # dirs_camera_intrisinc = os.listdir(path_camera_intrinsic)
    # # path_list_camera_intrisinc = get_files_path(path_camera_intrinsic, '.json')
    # # path_list_camera_intrinsic.sort()
    #
    # for frame in dirs_camera_intrinsic:
    index = img_path.split("/")[-1].split(".")[0]
    calib_intrinsic = get_cam_calib_intrinsic(path_camera_intrinsic)
    img = get_rgb(img_path)

    cam8points = np.array(camera_8_points_list)
    num_bbox = cam8points.shape[0]

    uv_origin = points_cam2img(cam8points, calib_intrinsic)
    uv_origin = (uv_origin - 1).round()

    plot_rect3d_on_img(img, num_bbox, uv_origin)
    cv2.imwrite(os.path.join(save_path, index + ".png"), img)
    print(index)

    return True
