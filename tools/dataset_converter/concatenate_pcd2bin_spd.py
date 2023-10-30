import numpy as np
from pypcd import pypcd
import os
import errno
import json
from tqdm import tqdm
import argparse


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def read_json(path_json):
    with open(path_json, "r") as load_f:
        my_json = json.load(load_f)
    return my_json


def concatenate_pcd2bin(path1, path2, path_save):
    pc1 = pypcd.PointCloud.from_path(path1)
    pc2 = pypcd.PointCloud.from_path(path2)

    np_x1 = (np.array(pc1.pc_data["x"], dtype=np.float32)).astype(np.float32)
    np_y1 = (np.array(pc1.pc_data["y"], dtype=np.float32)).astype(np.float32)
    np_z1 = (np.array(pc1.pc_data["z"], dtype=np.float32)).astype(np.float32)
    np_i1 = (np.array(pc1.pc_data["intensity"], dtype=np.float32)).astype(np.float32) / 255

    np_x2 = (np.array(pc2.pc_data["x"], dtype=np.float32)).astype(np.float32)
    np_y2 = (np.array(pc2.pc_data["y"], dtype=np.float32)).astype(np.float32)
    np_z2 = (np.array(pc2.pc_data["z"], dtype=np.float32)).astype(np.float32)
    np_i2 = (np.array(pc2.pc_data["intensity"], dtype=np.float32)).astype(np.float32) / 255

    np_x = np.append(np_x1, np_x2)
    np_y = np.append(np_y1, np_y2)
    np_z = np.append(np_z1, np_z2)
    np_i = np.append(np_i1, np_i2)

    points_32 = np.transpose(np.vstack((np_x, np_y, np_z, np_i)))
    points_32.tofile(path_save)


def concatenate_pcd_i_and_v(path_c, path_i2v, path_dest):
    mkdir_p(path_dest)

    path_c_data_info = os.path.join(path_c, "cooperative/data_info.json")
    c_data_info = read_json(path_c_data_info)

    for data in tqdm(c_data_info):
        path_pcd_v = os.path.join(path_c, "vehicle-side/velodyne", data["vehicle_frame"] + ".pcd")

        name_i = data["infrastructure_frame"] + ".pcd"
        path_pcd_i = os.path.join(path_i2v, name_i)

        name = data["vehicle_frame"] + ".bin"
        path_save = os.path.join(path_dest, name)
        concatenate_pcd2bin(path_pcd_i, path_pcd_v, path_save)


parser = argparse.ArgumentParser("Concat the Converted Infrastructure Point Cloud with Vehicle Point Cloud.")
parser.add_argument(
    "--source-root",
    type=str,
    default="./data/SPD/cooperative-vehicle-infrastructure",
    help="Raw data root about SPD-C.",
)
parser.add_argument(
    "--i2v-root",
    type=str,
    default="./data/SPD/cooperative-vehicle-infrastructure/vic3d-early-fusion/velodyne/lidar_i2v",
    help="The data root where the data with ego-vehicle coordinate is generated.",
)
parser.add_argument(
    "--target-root",
    type=str,
    default="./data/SPD/cooperative-vehicle-infrastructure/vic3d-early-fusion/velodyne-concated",
    help="The concated point cloud.",
)

if __name__ == "__main__":
    args = parser.parse_args()
    path_c = args.source_root
    path_i2v = args.i2v_root
    path_dest = args.target_root

    concatenate_pcd_i_and_v(path_c, path_i2v, path_dest)
