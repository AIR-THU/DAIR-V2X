import os
import argparse
import numpy as np
from rich.progress import track
from tools.dataset_converter.utils import read_json, write_json, inverse_matrix, trans_point, get_lidar_3d_8points, get_label_lidar_rotation, \
    get_camera_3d_alpha_rotation, get_cam_calib_intrinsic, get_lidar2camera, get_lidar2novatel, get_novatel2world, get_virtuallidar2world


def concat_txt(path_input, path_output, file_name_output):
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    path_file_output = path_output + '/' + file_name_output + '.txt'
    write_f = open(path_file_output, 'w')
    list_files = os.listdir(path_input)
    list_files.sort()
    for file in list_files:
        path_file_input = path_input + '/' + file
        with open(path_file_input, 'r') as read_f:
            list_lines = read_f.readlines()
            for line in list_lines:
                write_f.writelines(line)
    write_f.close()


def concat_kitti_label_txt(path_input):
    """
        Args:
            path_input: "../../data/KITTI/cooperative-vehicle-infrastructure/" + vi + "/" + tvt
        Returns:
            None
    """
    list_sequence = os.listdir(path_input)
    list_sequence.sort()
    for sequence in track(list_sequence):
        path_input_label = path_input + '/' + sequence + '/label_02_i2v_split'
        path_output_label = path_input + '/' + sequence + '/label_02_i2v'
        concat_txt(path_input_label, path_output_label, sequence)


def gen_label_track_i2v(kitti_target_root):
    for tvt in ["training", "validation", "testing"]:
        input_path = kitti_target_root + '/' + tvt
        concat_kitti_label_txt(input_path)


def get_frame_data_info(data_info, frame_id):
    for data in data_info:
        if data["frame_id"] == frame_id:
            return data


def trans_points_cam2img(camera_3d_8_points, calib_intrinsic, with_depth=False):
    """
        Project points from camera coordicates to image coordinates.
        Args:
            camera_3d_8_points: list(8, 3)
            calib_intrinsic: np.array(3, 4)
        Returns:
            list(8, 2)
    """
    camera_3d_8_points = np.array(camera_3d_8_points)
    points_shape = np.array([8, 1])
    points_4 = np.concatenate((camera_3d_8_points, np.ones(points_shape)), axis=-1)
    point_2d = np.dot(calib_intrinsic, points_4.T)
    point_2d = point_2d.T
    point_2d_res = point_2d[:, :2] / point_2d[:, 2:3]
    if with_depth:
        return np.cat([point_2d_res, point_2d[..., 2:3]], dim=-1)
    return point_2d_res.tolist()


def trans_point_i2v(input_point, path_virtuallidar2world, path_novatel2world, path_lidar2novatel, delta_x, delta_y):
    # virtuallidar to world
    rotation, translation = get_virtuallidar2world(path_virtuallidar2world)
    point = trans_point(input_point, translation, rotation)

    # world to novatel
    rotation, translation = get_novatel2world(path_novatel2world)
    new_rotation = inverse_matrix(rotation)
    new_translation = - np.dot(new_rotation, translation)
    point = trans_point(point, new_translation, new_rotation)

    # novatel to lidar
    rotation, translation = get_lidar2novatel(path_lidar2novatel)
    new_rotation = inverse_matrix(rotation)
    new_translation = - np.dot(new_rotation, translation)
    point = trans_point(point, new_translation, new_rotation)

    point = np.array(point).reshape(3, 1) + np.array([delta_x, delta_y, 0]).reshape(3, 1)
    point = point.reshape(1, 3).tolist()[0]

    return point


def trans_label_i2v(dair_inf_label_path, dair_target_label_file, kitti_target_label_file, virtuallidar2world_path,
                    novatel2world_path, lidar2novatel_path, lidar2camera_path, camera2image_path, delta_x, delta_y,
                    pointcloud_timestamp):
    dair_inf_label_data = read_json(dair_inf_label_path)
    r_lidar2camera, t_lidar2camera = get_lidar2camera(lidar2camera_path)
    calib_intrinsic = get_cam_calib_intrinsic(camera2image_path)
    save_file = open(kitti_target_label_file, 'w')
    frame = kitti_target_label_file.split('/')[-1].split('.')[0]
    for m in range(len(dair_inf_label_data)):
        # 提取每个目标的信息
        i_label_3d_dimensions = [float(dair_inf_label_data[m]["3d_dimensions"]["l"]),
                                 float(dair_inf_label_data[m]["3d_dimensions"]["w"]),
                                 float(dair_inf_label_data[m]["3d_dimensions"]["h"])]
        i_label_lidar_3d_location = [float(dair_inf_label_data[m]["3d_location"]["x"]),
                                     float(dair_inf_label_data[m]["3d_location"]["y"]),
                                     float(dair_inf_label_data[m]["3d_location"]["z"])]
        i_label_lidar_rotation = dair_inf_label_data[m]["rotation"]

        # 生成车端lidar和camera坐标系下目标的中心点坐标v_label_lidar_3d_location, v_label_camera_3d_location
        v_label_lidar_3d_location = trans_point_i2v(i_label_lidar_3d_location, virtuallidar2world_path, novatel2world_path,
                                                    lidar2novatel_path, delta_x, delta_y)
        v_label_camera_3d_location = trans_point(v_label_lidar_3d_location, t_lidar2camera, r_lidar2camera)
        v_label_camera_3d_location[1] = v_label_camera_3d_location[1] + float(dair_inf_label_data[m]["3d_dimensions"]["h"]) / 2

        # 生成车端坐标系下目标的8个角点坐标
        list_i_lidar_3d_8_points = get_lidar_3d_8points(i_label_3d_dimensions, i_label_lidar_3d_location, i_label_lidar_rotation)
        list_v_lidar_3d_8_points = []
        list_v_camera_3d_8_points = []
        for i_lidar_point in list_i_lidar_3d_8_points:
            # 投影到车端lidar坐标系
            v_lidar_point = trans_point_i2v(i_lidar_point, virtuallidar2world_path, novatel2world_path, lidar2novatel_path,
                                            delta_x, delta_y)
            list_v_lidar_3d_8_points.append(v_lidar_point)
            # 投影到车端camera坐标系
            v_camera_point = trans_point(v_lidar_point, t_lidar2camera, r_lidar2camera)
            list_v_camera_3d_8_points.append(v_camera_point)

        # 生成车端lidar坐标系下目标的偏航角v_label_lidar_rotation
        v_label_lidar_rotation = get_label_lidar_rotation(list_v_lidar_3d_8_points)
        # 生成车端lidar坐标系下目标的alpha和偏航角rotation_y
        alpha, i_label_camera_rotation = get_camera_3d_alpha_rotation(list_v_camera_3d_8_points, v_label_camera_3d_location)

        # 投影到车端图像坐标系
        v_label_image_8_points_2d = trans_points_cam2img(list_v_camera_3d_8_points, calib_intrinsic)
        x_max = max(v_label_image_8_points_2d[:][0])
        x_min = min(v_label_image_8_points_2d[:][0])
        y_max = max(v_label_image_8_points_2d[:][1])
        y_min = min(v_label_image_8_points_2d[:][1])

        # 更新路端投影到车端的目标信息
        dair_inf_label_data[m]["alpha"] = alpha
        dair_inf_label_data[m]["3d_location"]["x"] = v_label_lidar_3d_location[0]
        dair_inf_label_data[m]["3d_location"]["y"] = v_label_lidar_3d_location[1]
        dair_inf_label_data[m]["3d_location"]["z"] = v_label_lidar_3d_location[2]
        dair_inf_label_data[m]["rotation"] = v_label_lidar_rotation

        # 更新贴合camera的label的image 2d信息
        dair_inf_label_data[m]["2d_box"]["xmin"] = x_min
        dair_inf_label_data[m]["2d_box"]["ymin"] = y_min
        dair_inf_label_data[m]["2d_box"]["xmax"] = x_max
        dair_inf_label_data[m]["2d_box"]["ymax"] = y_max
        # 保存车端label投影到路端的label文件

        # 生成 kitti label
        list_kitti_label = [frame, dair_inf_label_data[m]["type"], str(dair_inf_label_data[m]["track_id"]),
                            str(dair_inf_label_data[m]["truncated_state"]),
                            str(dair_inf_label_data[m]["occluded_state"]), str(dair_inf_label_data[m]["alpha"]),
                            str(dair_inf_label_data[m]["2d_box"]["xmin"]),
                            str(dair_inf_label_data[m]["2d_box"]["ymin"]), str(dair_inf_label_data[m]["2d_box"]["xmax"]),
                            str(dair_inf_label_data[m]["2d_box"]["ymax"]), str(dair_inf_label_data[m]["3d_dimensions"]["h"]),
                            str(dair_inf_label_data[m]["3d_dimensions"]["w"]), str(dair_inf_label_data[m]["3d_dimensions"]["l"]),
                            str(v_label_camera_3d_location[0]), str(v_label_camera_3d_location[1]),
                            str(v_label_camera_3d_location[2]),
                            str(i_label_camera_rotation), str(dair_inf_label_data[m]["3d_location"]["x"]),
                            str(dair_inf_label_data[m]["3d_location"]["y"]), str(dair_inf_label_data[m]["3d_location"]["z"]),
                            str(dair_inf_label_data[m]["rotation"]), pointcloud_timestamp, "1", "1", dair_inf_label_data[m]["token"] + '\n']
        str_kitti_label = ' '.join(list_kitti_label)
        save_file.writelines(str_kitti_label)
    write_json(dair_target_label_file, dair_inf_label_data)
    save_file.close()


def get_i2v(dair_source_path, dair_target_path, kitti_target_path, split_info, label_type):
    dict_sequence2tvt = {}
    for tvt in [["train", "training"], ["val", "validation"], ["test", "testing"]]:
        for seq in split_info["batch_split"][tvt[0]]:
            dict_sequence2tvt[seq] = tvt[1]

    inf_label_type = label_type.replace("lidar", "virtuallidar")
    dair_target_label_path = f'{dair_target_path}/label_i2v/{inf_label_type}'
    if not os.path.exists(dair_target_label_path):
        os.makedirs(dair_target_label_path)

    coop_data_info_path = f'{dair_source_path}/cooperative/data_info.json'
    coop_data_info = read_json(coop_data_info_path)
    inf_data_info_path = f'{dair_source_path}/infrastructure-side/data_info.json'
    inf_data_info = read_json(inf_data_info_path)

    for i in track(coop_data_info):

        virtuallidar2world_path = f'{dair_source_path}/infrastructure-side/calib/virtuallidar_to_world/{i["infrastructure_frame"]}.json'
        novatel2world_path = f'{dair_source_path}/vehicle-side/calib/novatel_to_world/{i["vehicle_frame"]}.json'
        lidar2novatel_path = f'{dair_source_path}/vehicle-side/calib/lidar_to_novatel/{i["vehicle_frame"]}.json'
        lidar2camera_path = f'{dair_source_path}/vehicle-side/calib/lidar_to_camera/{i["vehicle_frame"]}.json'
        camera2image_path = f'{dair_source_path}/vehicle-side/calib/camera_intrinsic/{i["vehicle_frame"]}.json'
        delta_x = i["system_error_offset"]["delta_x"]
        delta_y = i["system_error_offset"]["delta_y"]

        # 转换label文件
        dair_inf_label_path = f'{dair_source_path}/infrastructure-side/label/{inf_label_type}/{i["infrastructure_frame"]}.json'
        dair_target_label_file = f'{dair_target_label_path}/{i["vehicle_frame"]}.json'
        kitti_target_label_path = f'{kitti_target_path}/{dict_sequence2tvt[i["infrastructure_sequence"]]}/{i["infrastructure_sequence"]}/label_02_i2v_split'
        if not os.path.exists(kitti_target_label_path):
            os.makedirs(kitti_target_label_path)
        kitti_target_label_file = f'{kitti_target_label_path}/{i["infrastructure_frame"]}.txt'
        for j in inf_data_info:
            if j["frame_id"] == i["infrastructure_frame"]:
                pointcloud_timestamp = j["pointcloud_timestamp"]
        trans_label_i2v(dair_inf_label_path, dair_target_label_file, kitti_target_label_file, virtuallidar2world_path,
                        novatel2world_path, lidar2novatel_path, lidar2camera_path, camera2image_path, delta_x, delta_y,
                        pointcloud_timestamp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Convert The Label from Infrastructure-side to Vehicle-side")
    parser.add_argument(
        "--dair-source-root",
        type=str,
        default="../../data/SPD/cooperative-vehicle-infrastructure",
        help="Raw data root about DAIR-V2X-C"
    )
    parser.add_argument(
        "--dair-target-root",
        type=str,
        default="../../data/SPD/cooperative-vehicle-infrastructure/infrastructure-side",
        help="The dair format infrastructure-side data root",
    )
    parser.add_argument(
        "--kitti-target-root",
        type=str,
        default="../../data/KITTI/cooperative-vehicle-infrastructure/infrastructure-side",
        help="The kitti format infrastructure-side data root",
    )
    parser.add_argument(
        "--split-path",
        type=str,
        default="../../data/split_datas/cooperative-split-data-spd.json",
        help="Json file to split the data into training/validation/testing."
    )
    parser.add_argument("--label-type", type=str, default="lidar", help="label type from ['lidar', 'camera']")
    args = parser.parse_args()
    dair_source_root = args.dair_source_root
    dair_target_root = args.dair_target_root
    kitti_target_root = args.kitti_target_root
    split_path = args.split_path
    split_info = read_json(split_path)
    label_type = args.label_type

    get_i2v(dair_source_root, dair_target_root, kitti_target_root, split_info, label_type)
    gen_label_track_i2v(kitti_target_root)
