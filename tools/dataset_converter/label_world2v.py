import os
import numpy as np
from tqdm import tqdm
import math
import argparse
from gen_kitti.utils import read_json, write_json, mkdir_p

"""
            virtuallidar2world
inf lidar ------------------------> world coordinate <===== label_world
              补充   relative error      ^
                                         |
                                         |
                                         |
                                         |
                                         | novatel2world
                                         |
                                         |
                                         |
                                         |
                 lidar2novatel           |
veh lidar --------------------------> novatel

"""


"""
   (x0y0z0, x0y0z1, x0y1z1, x0y1z0, x1y0z0, x1y0z1, x1y1z1, x1y1z0)

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


def get_3d_location(data_label_world):
    x = data_label_world["3d_location"]["x"]
    y = data_label_world["3d_location"]["y"]
    z = data_label_world["3d_location"]["z"]
    point = np.array([x, y, z]).reshape(3, 1)
    return point


def write_3d_location(point):
    x = float(point[0])
    y = float(point[1])
    z = float(point[2])
    return x, y, z


def get_world_8_points(data_label_world):
    world_8_points = data_label_world["world_8_points"]
    points = []
    for i in range(8):
        point = np.array(world_8_points[i]).reshape(3, 1)
        points.append(point)
    return points


def write_world_8_points(points):
    my_points = []
    for i in range(8):
        point = np.array(points[i]).reshape(1, 3).tolist()[0]
        my_points.append(point)
    return my_points


def get_novatel2world(path_novatel2world):
    novatel2world = read_json(path_novatel2world)
    rotation = novatel2world["rotation"]
    translation = novatel2world["translation"]
    return rotation, translation


def get_lidar2novatel(path_lidar2novatel):
    lidar2novatel = read_json(path_lidar2novatel)
    rotation = lidar2novatel["transform"]["rotation"]
    translation = lidar2novatel["transform"]["translation"]
    return rotation, translation


def get_data(data_info, path_pcd):
    for data in data_info:
        name1 = os.path.split(path_pcd)[-1]
        name2 = os.path.split(data["pointcloud_path"])[-1]
        if name1 == name2:
            return data


def trans(input_point, translation, rotation):
    input_point = np.array(input_point).reshape(3, 1)
    translation = np.array(translation).reshape(3, 1)
    rotation = np.array(rotation).reshape(3, 3)
    output_point = np.dot(rotation, input_point).reshape(3, 1) + np.array(translation).reshape(3, 1)
    return output_point


def rev_matrix(R):
    R = np.matrix(R)
    rev_R = R.I
    rev_R = np.array(rev_R)
    return rev_R


def trans_point_world2v(point, path_novatel2world, path_lidar2novatel):
    # world to novatel
    rotation, translation = get_novatel2world(path_novatel2world)
    new_rotation = rev_matrix(rotation)
    new_translation = -np.dot(new_rotation, translation)
    point = trans(point, new_translation, new_rotation)

    # novatel to lidar
    rotation, translation = get_lidar2novatel(path_lidar2novatel)
    new_rotation = rev_matrix(rotation)
    new_translation = -np.dot(new_rotation, translation)
    point = trans(point, new_translation, new_rotation)

    point = point.reshape(1, 3).tolist()
    point = point[0]

    return point


def label_world2v(path_cooperative_label, path_novatel2world, path_lidar2novatel):
    label_world = read_json(path_cooperative_label)
    new_label = []

    for i in range(len(label_world)):
        my_3d_point = get_3d_location(label_world[i])
        new_3d_point = trans_point_world2v(my_3d_point, path_novatel2world, path_lidar2novatel)

        world_8_points = get_world_8_points(label_world[i])
        my_world_8_points = []
        for j in range(8):
            point = world_8_points[j]
            point = trans_point_world2v(point, path_novatel2world, path_lidar2novatel)
            my_world_8_points.append(point)
        new_world_8_points = write_world_8_points(my_world_8_points)

        length = label_world[i]["3d_dimensions"]["l"]
        w = label_world[i]["3d_dimensions"]["w"]
        rotation = get_rotation(new_world_8_points, new_3d_point, length, w)

        label_world[i]["3d_location"]["x"] = new_3d_point[0]
        label_world[i]["3d_location"]["y"] = new_3d_point[1]
        label_world[i]["3d_location"]["z"] = new_3d_point[2]
        label_world[i]["rotation"] = rotation
        label_world[i]["world_8_points"] = new_world_8_points

        new_label.append(label_world[i])
    return new_label


def get_rotation(world_8_points, my_3d_point, length, w):
    x = my_3d_point[0]
    a = world_8_points[0][0]
    b = world_8_points[1][0]
    c = world_8_points[2][0]
    r_tan = ((b + c - 2 * x) * length) / ((a + b - 2 * x) * w)
    rotation = math.atan(r_tan)
    return rotation


def gen_new_label(path_cooperative_label, path_novatel2world, path_lidar2novatel, path_save):
    new_label = label_world2v(path_cooperative_label, path_novatel2world, path_lidar2novatel)
    write_json(path_save, new_label)


def get_label2v(path_c, path_dest):
    mkdir_p(path_dest)
    path_c_data_info = os.path.join(path_c, "cooperative/data_info.json")
    path_v_data_info = os.path.join(path_c, "vehicle-side/data_info.json")
    c_data_info = read_json(path_c_data_info)
    v_data_info = read_json(path_v_data_info)

    for data in tqdm(c_data_info):
        path_pcd_v = os.path.join(path_c, data["vehicle_pointcloud_path"])
        path_cooperative_label = os.path.join(path_c, data["cooperative_label_path"])

        v_data = get_data(v_data_info, path_pcd_v)
        path_novatel2world = os.path.join(path_c, "vehicle-side", v_data["calib_novatel_to_world_path"])
        path_lidar2novatel = os.path.join(path_c, "vehicle-side", v_data["calib_lidar_to_novatel_path"])

        name = os.path.split(path_cooperative_label)[-1]
        path_save = os.path.join(path_dest, name)
        gen_new_label(path_cooperative_label, path_novatel2world, path_lidar2novatel, path_save)


parser = argparse.ArgumentParser("Generate label from world coordinate to vehicle lidar coordinate.")
parser.add_argument(
    "--source-root",
    type=str,
    default="./data/cooperative-vehicle-infrastructure",
    help="Raw data root about DAIR-V2X-C.",
)
parser.add_argument(
    "--target-root",
    type=str,
    default="./label_new",
    help="The label root where the label is in vehicle lidar coordinate system.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    source_root = args.source_root
    target_label_root = args.target_root
    get_label2v(source_root, target_label_root)
