import os
import json
import argparse
import numpy as np
from pypcd import pypcd
import open3d as o3d
from tqdm import tqdm
import errno


def read_json(path_json):
    with open(path_json, 'r') as load_f:
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


def get_virtuallidar2world(path_virtuallidar2world):
    virtuallidar2world = read_json(path_virtuallidar2world)
    rotation = virtuallidar2world['rotation']
    translation = virtuallidar2world['translation']
    return rotation, translation


def get_novatel2world(path_novatel2world):
    novatel2world = read_json(path_novatel2world)
    rotation = novatel2world['rotation']
    translation = novatel2world['translation']
    return rotation, translation


def get_lidar2novatel(path_lidar2novatel):
    lidar2novatel = read_json(path_lidar2novatel)
    rotation = lidar2novatel['transform']['rotation']
    translation = lidar2novatel['transform']['translation']
    return rotation, translation


def get_data(data_info, frame_id):
    for data in data_info:
        if data["frame_id"] == frame_id:
            return data


def trans(input_point, translation, rotation):
    input_point = np.array(input_point).reshape(3, -1)
    translation = np.array(translation).reshape(3, 1)
    rotation = np.array(rotation).reshape(3, 3)
    output_point = np.dot(rotation, input_point).reshape(3, -1) + np.array(translation).reshape(3, 1)
    return output_point


def rev_matrix(R):
    R = np.matrix(R)
    rev_R = R.I
    rev_R = np.array(rev_R)
    return rev_R


def trans_point_i2v(input_point, path_virtuallidar2world, path_novatel2world, path_lidar2novatel, delta_x, delta_y):
    # print('0:', input_point)

    # virtuallidar to world
    rotation, translation = get_virtuallidar2world(path_virtuallidar2world)
    point = trans(input_point, translation, rotation)
    '''
    print('rotation, translation, delta_x, delta_y', rotation, translation, delta_x, delta_y)
    print('1:', point)
    '''

    # world to novatel
    rotation, translation = get_novatel2world(path_novatel2world)
    new_rotation = rev_matrix(rotation)
    new_translation = - np.dot(new_rotation, translation)
    point = trans(point, new_translation, new_rotation)
    '''
    print('rotation, translation:', rotation, translation)
    print('new_translation, new_rotation:', new_translation, new_rotation)
    print('2:', point)
    '''

    # novatel to lidar
    rotation, translation = get_lidar2novatel(path_lidar2novatel)
    new_rotation = rev_matrix(rotation)
    new_translation = - np.dot(new_rotation, translation)
    point = trans(point, new_translation, new_rotation) + np.array([delta_x, delta_y, 0]).reshape(3, 1)
    '''
    print('rotation, translation:', rotation, translation)
    print('new_translation, new_rotation:', new_translation, new_rotation)
    print('3:', point)
    '''
    # point = point.reshape(1, 3).tolist()
    # point = point[0]
    point = point.T
    
    return point


def read_pcd(path_pcd):
    pointpillar = o3d.io.read_point_cloud(path_pcd)
    points = np.asarray(pointpillar.points)
    # points = points.tolist()
    return points


def show_pcd(path_pcd):
    pcd = read_pcd(path_pcd)
    o3d.visualization.draw_geometries([pcd])


def write_pcd(path_pcd, new_points, path_save):
    pc = pypcd.PointCloud.from_path(path_pcd)
    pc.pc_data['x'] = np.array([a[0] for a in new_points])
    pc.pc_data['y'] = np.array([a[1] for a in new_points])
    pc.pc_data['z'] = np.array([a[2] for a in new_points])
    pc.save_pcd(path_save, compression='binary_compressed')


def trans_pcd_i2v(path_pcd, path_virtuallidar2world, path_novatel2world, path_lidar2novatel, delta_x, delta_y, path_save):
    # (n, 3)
    points = read_pcd(path_pcd)
    # (n, 3)
    new_points = trans_point_i2v(points.T, path_virtuallidar2world, path_novatel2world, path_lidar2novatel, delta_x, delta_y)
    write_pcd(path_pcd, new_points, path_save)


def get_i2v(path_c, path_dest):
    mkdir_p(path_dest)
    path_c_data_info = os.path.join(path_c, 'cooperative/data_info.json')
    path_i_data_info = os.path.join(path_c, 'infrastructure-side/data_info.json')
    path_v_data_info = os.path.join(path_c, 'vehicle-side/data_info.json')
    c_data_info = read_json(path_c_data_info)
    i_data_info = read_json(path_i_data_info)
    v_data_info = read_json(path_v_data_info)

    # for data in tqdm(c_data_info):
    for data in tqdm(c_data_info):
        i_data = get_data(i_data_info, data["infrastructure_frame"])
        v_data = get_data(v_data_info, data["vehicle_frame"])
        path_pcd_i = os.path.join(path_c, "infrastructure-side/velodyne", data["infrastructure_frame"] + ".pcd")
        path_virtuallidar2world = os.path.join(path_c, 'infrastructure-side', i_data['calib_virtuallidar_to_world_path'])
        path_novatel2world = os.path.join(path_c, 'vehicle-side', v_data['calib_novatel_to_world_path'])
        path_lidar2novatel = os.path.join(path_c, 'vehicle-side', v_data['calib_lidar_to_novatel_path'])
        name = os.path.split(path_pcd_i)[-1]
        path_save = os.path.join(path_dest, name)
        delta_x = data["system_error_offset"]["delta_x"]
        delta_y = data["system_error_offset"]["delta_y"]
        trans_pcd_i2v(path_pcd_i, path_virtuallidar2world, path_novatel2world, path_lidar2novatel, delta_x, delta_y, path_save)


parser = argparse.ArgumentParser("Convert The Point Cloud from Infrastructure to Ego-vehicle")
parser.add_argument("--source-root",
                    type=str,
                    default="./data/SPD",
                    help="Raw data root about SPD.")
parser.add_argument(
    "--target-root",
    type=str,
    default="./data/SPD/vic3d-early-fusion/velodyne/lidar_i2v",
    help="The data root where the data with ego-vehicle coordinate is generated",
)

if __name__ == "__main__":
    args = parser.parse_args()
    source_root = args.source_root
    target_root = args.target_root

    get_i2v(source_root, target_root)