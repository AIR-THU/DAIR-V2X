import os
import numpy as np
from rich.progress import track
from tools.dataset_converter.utils import read_json, inverse_matrix, get_lidar2camera, get_lidar2novatel, get_cam_calib_intrinsic


def convert_calib_dair2kitti(cam_intrinsic, r_velo2cam, t_velo2cam, r_novatel2velo, t_novatel2velo):
    P2 = cam_intrinsic.reshape(12, order="C")

    Tr_velo_to_cam = np.concatenate((r_velo2cam, t_velo2cam), axis=1)
    Tr_velo_to_cam = Tr_velo_to_cam.reshape(12, order="C")

    Tr_imu_to_velo = np.concatenate((r_novatel2velo, t_novatel2velo), axis=1)
    Tr_imu_to_velo = Tr_imu_to_velo.reshape(12, order="C")

    return P2, Tr_velo_to_cam, Tr_imu_to_velo


def gen_calib2kitti(source_root, target_root, dict_sequence2tvt, sensor_view):
    data_info = read_json(f'{source_root}/data_info.json')
    for i in track(data_info):
        target_calib_path = f'{target_root}/{dict_sequence2tvt[i["sequence_id"]]}/{i["sequence_id"]}/calib'
        if not os.path.exists(target_calib_path):
            os.makedirs(target_calib_path)
        target_calib_file_path = f'{target_calib_path}/{i["frame_id"]}.txt'
        calib_camera_intrinsic_path = f'{source_root}/{i["calib_camera_intrinsic_path"]}'
        cam_intrinsic = get_cam_calib_intrinsic(calib_camera_intrinsic_path)
        if sensor_view == "vehicle":
            calib_lidar_to_camera_path = f'{source_root}/{i["calib_lidar_to_camera_path"]}'
            r_velo2cam, t_velo2cam = get_lidar2camera(calib_lidar_to_camera_path)
            calib_lidar_to_novatel_path = f'{source_root}/{i["calib_lidar_to_novatel_path"]}'
            r_velo2imu, t_velo2imu = get_lidar2novatel(calib_lidar_to_novatel_path)
            r_imu2velo = inverse_matrix(r_velo2imu)
            t_imu2velo = - np.dot(r_imu2velo, t_velo2imu)
        else:
            calib_lidar_to_camera_path = f'{source_root}/{i["calib_virtuallidar_to_camera_path"]}'
            r_velo2cam, t_velo2cam = get_lidar2camera(calib_lidar_to_camera_path)
            r_imu2velo = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            t_imu2velo = - np.array([[0], [0], [0]])

        P2, Tr_velo_to_cam, Tr_imu_to_velo = convert_calib_dair2kitti(cam_intrinsic, r_velo2cam, t_velo2cam, r_imu2velo, t_imu2velo)

        str_P2 = "P2: "
        str_Tr_velo_to_cam = "Tr_velo_to_cam: "
        str_Tr_imu_to_velo = "Tr_imu_to_velo: "
        for m in range(11):
            str_P2 = str_P2 + str(P2[m]) + " "
            str_Tr_velo_to_cam = str_Tr_velo_to_cam + str(Tr_velo_to_cam[m]) + " "
            str_Tr_imu_to_velo = str_Tr_imu_to_velo + str(Tr_imu_to_velo[m]) + " "
        str_P2 = str_P2 + str(P2[11])
        str_Tr_velo_to_cam = str_Tr_velo_to_cam + str(Tr_velo_to_cam[11])
        str_Tr_imu_to_velo = str_Tr_imu_to_velo + str(Tr_imu_to_velo[11])

        str_P0 = str_P2.replace("P2", "P0")
        str_P1 = str_P2.replace("P2", "P1")
        str_P3 = str_P2.replace("P2", "P3")
        str_R0_rect = "R0_rect: 1 0 0 0 1 0 0 0 1"

        with open(target_calib_file_path, "w") as save_file:
            gt_line = (
                    str_P0
                    + "\n"
                    + str_P1
                    + "\n"
                    + str_P2
                    + "\n"
                    + str_P3
                    + "\n"
                    + str_R0_rect
                    + "\n"
                    + str_Tr_velo_to_cam
                    + "\n"
                    + str_Tr_imu_to_velo
            )
            save_file.write(gt_line)
