import os
import numpy as np
import argparse
from pypcd import pypcd
from gen_kitti.utils import read_json, write_json, pcd2bin
import json


def get_calibs(calib_path):
    calib = read_json(calib_path)
    if "transform" in calib.keys():
        calib = calib["transform"]
    rotation = calib["rotation"]
    translation = calib["translation"]
    return rotation, translation


def rev_matrix(rotation, translation):
    rotation = np.matrix(rotation)
    rev_R = rotation.I
    rev_R = np.array(rev_R)
    rev_T = -np.dot(rev_R, translation)

    return rev_R, rev_T


def mul_matrix(rotation_1, translation_1, rotation_2, translation_2):
    rotation_1 = np.matrix(rotation_1)
    translation_1 = np.matrix(translation_1)
    rotation_2 = np.matrix(rotation_2)
    translation_2 = np.matrix(translation_2)

    rotation = rotation_2 * rotation_1
    translation = rotation_2 * translation_1 + translation_2
    rotation = np.array(rotation)
    translation = np.array(translation)

    return rotation, translation


def trans_lidar_i2v(inf_lidar2world_path, veh_lidar2novatel_path, veh_novatel2world_path, system_error_offset=None):
    inf_lidar2world_r, inf_lidar2world_t = get_calibs(inf_lidar2world_path)
    if system_error_offset is not None:
        inf_lidar2world_t[0][0] = inf_lidar2world_t[0][0] + system_error_offset["delta_x"]
        inf_lidar2world_t[1][0] = inf_lidar2world_t[1][0] + system_error_offset["delta_y"]

    veh_novatel2world_r, veh_novatel2world_t = get_calibs(veh_novatel2world_path)
    veh_world2novatel_r, veh_world2novatel_t = rev_matrix(veh_novatel2world_r, veh_novatel2world_t)
    inf_lidar2novatel_r, inf_lidar2novatel_t = mul_matrix(
        inf_lidar2world_r, inf_lidar2world_t, veh_world2novatel_r, veh_world2novatel_t
    )

    veh_lidar2novatel_r, veh_lidar2novatel_t = get_calibs(veh_lidar2novatel_path)
    veh_novatel2lidar_r, veh_novatel2lidar_t = rev_matrix(veh_lidar2novatel_r, veh_lidar2novatel_t)
    inf_lidar2lidar_r, inf_lidar2lidar_t = mul_matrix(
        inf_lidar2novatel_r, inf_lidar2novatel_t, veh_novatel2lidar_r, veh_novatel2lidar_t
    )

    return inf_lidar2lidar_r, inf_lidar2lidar_t


def trans_point(input_point, rotation, translation):
    input_point = np.array(input_point).reshape(3, 1)
    translation = np.array(translation).reshape(3, 1)
    rotation = np.array(rotation).reshape(3, 3)
    output_point = np.dot(rotation, input_point).reshape(3, 1) + np.array(translation).reshape(3, 1)
    return output_point


parser = argparse.ArgumentParser("Generate label from world coordinate to vehicle lidar coordinate.")
parser.add_argument(
    "--source-root", type=str, default="data/cooperative-vehicle-infrastructure", help="Raw data root about DAIR-V2X-C."
)


if __name__ == "__main__":
    args = parser.parse_args()
    dair_v2x_c_root = args.source_root
    c_jsons_path = os.path.join(dair_v2x_c_root, "cooperative/data_info.json")
    c_jsons = read_json(c_jsons_path)

    for c_json in c_jsons:
        inf_idx = c_json["infrastructure_image_path"].split("/")[-1].replace(".jpg", "")
        inf_lidar2world_path = os.path.join(
            dair_v2x_c_root, "infrastructure-side/calib/virtuallidar_to_world/" + inf_idx + ".json"
        )
        veh_idx = c_json["vehicle_image_path"].split("/")[-1].replace(".jpg", "")
        veh_lidar2novatel_path = os.path.join(
            dair_v2x_c_root, "vehicle-side/calib/lidar_to_novatel/" + veh_idx + ".json"
        )
        veh_novatel2world_path = os.path.join(
            dair_v2x_c_root, "vehicle-side/calib/novatel_to_world/" + veh_idx + ".json"
        )
        system_error_offset = c_json["system_error_offset"]
        if system_error_offset == "":
            system_error_offset = None
        calib_lidar_i2v_r, calib_lidar_i2v_t = trans_lidar_i2v(
            inf_lidar2world_path, veh_lidar2novatel_path, veh_novatel2world_path, system_error_offset
        )
        print("calib_lidar_i2v: ", calib_lidar_i2v_r, calib_lidar_i2v_t)
        calib_lidar_i2v = {}
        calib_lidar_i2v["rotation"] = calib_lidar_i2v_r.tolist()
        calib_lidar_i2v["translation"] = calib_lidar_i2v_t.tolist()
        calib_lidar_i2v_save_path = os.path.join(dair_v2x_c_root, "cooperative/calib/lidar_i2v/" + veh_idx + ".json")
        with open(calib_lidar_i2v_save_path, "w") as f:
            json.dump(calib_lidar_i2v, f)

        """Convert the pointcloud from infrastructure lidar coordinate to vehicle coordinate
        inf_pcd_path = os.path.join(dair_v2x_c_root, c_json["infrastructure_pointcloud_path"])
        inf_pcd = pypcd.PointCloud.from_path(inf_pcd_path)
        for ii in range(len(inf_pcd.pc_data["x"])):
            np_x = inf_pcd.pc_data["x"][ii]
            np_y = inf_pcd.pc_data["y"][ii]
            np_z = inf_pcd.pc_data["z"][ii]
            inf_point = np.array([np_x, np_y, np_z])
            i2v_point = trans_point(inf_point, calib_lidar_i2v_r, calib_lidar_i2v_t)
            inf_pcd.pc_data["x"][ii] = i2v_point[0]
            inf_pcd.pc_data["y"][ii] = i2v_point[1]
            inf_pcd.pc_data["z"][ii] = i2v_point[2]
            inf_pcd.pc_data["intensity"][ii] = inf_pcd.pc_data["intensity"][ii] / 255
        i2v_pcd_save_path = os.path.join(dair_v2x_c_root, "cooperative/velodyne_i2v/" + veh_idx + ".pcd")
        pypcd.save_point_cloud(inf_pcd, i2v_pcd_save_path)
        i2v_bin_save_path = os.path.join(dair_v2x_c_root, "cooperative/velodyne_i2v/" + veh_idx + ".bin")
        pcd2bin(i2v_pcd_save_path, i2v_bin_save_path)

        pcd_path = os.path.join(dair_v2x_c_root, "infrastructure-side/velodyne/" + inf_idx + ".pcd")
        bin_save_path = os.path.join(dair_v2x_c_root, "infrastructure-side/velodyne/" + inf_idx + ".bin")
        pcd2bin(pcd_path, bin_save_path)

        pcd_path = os.path.join(dair_v2x_c_root, "vehicle-side/velodyne/" + veh_idx + ".pcd")
        bin_save_path = os.path.join(dair_v2x_c_root, "vehicle-side/velodyne/" + veh_idx + ".bin")
        pcd2bin(pcd_path, bin_save_path)
        """
