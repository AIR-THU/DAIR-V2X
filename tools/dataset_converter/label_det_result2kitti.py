import os
import math
import pickle
import numpy as np
from tqdm import tqdm
#from tools.dataset_converter.utils import read_json, trans_point, get_lidar2camera, get_cam_calib_intrinsic, get_label_lidar_rotation, get_camera_3d_alpha_rotation
from utils import read_json, trans_point, get_lidar2camera, get_cam_calib_intrinsic, get_label_lidar_rotation, get_camera_3d_alpha_rotation
import argparse

type2id = {
    "Car": 2,
    "Van": 2,
    "Truck": 2,
    "Bus": 2,
    "Cyclist": 1,
    "Tricyclist": 3,
    "Motorcyclist": 3,
    "Barrow": 3,
    "Barrowlist": 3,
    "Pedestrian": 0,
    "Trafficcone": 3,
    "Pedestrianignore": 3,
    "Carignore": 3,
    "otherignore": 3,
    "unknowns_unmovable": 3,
    "unknowns_movable": 3,
    "unknown_unmovable": 3,
    "unknown_movable": 3,
}

id2type = {
    0: "Pedestrian",
    1: "Cyclist",
    2: "Car",
    3: "Motorcyclist"
}


def get_sequence_id(frame, data_info):
    for obj in data_info:
        if frame == obj["frame_id"]:
            sequence_id = obj["sequence_id"]
            return sequence_id


def trans_points_cam2img(camera_3d_8points, calib_intrinsic, with_depth=False):
    """
        Transform points from camera coordinates to image coordinates.
        Args:
            camera_3d_8points: list(8, 3)
            calib_intrinsic: np.array(3, 4)
        Returns:
            list(8, 2)
    """
    camera_3d_8points = np.array(camera_3d_8points)
    points_shape = np.array([8, 1])
    points_4 = np.concatenate((camera_3d_8points, np.ones(points_shape)), axis=-1)
    point_2d = np.dot(calib_intrinsic, points_4.T)
    point_2d = point_2d.T
    point_2d_res = point_2d[:, :2] / point_2d[:, 2:3]
    if with_depth:
        return np.cat([point_2d_res, point_2d[..., 2:3]], dim=-1)
    return point_2d_res.tolist()


def label_det_result2kitti(input_file_path, output_dir_path, spd_path):
    """
        Convert detection results from mmdetection3d_kitti format to KITTI format.
        Args:
            input_file_path: mmdetection3d_kitti results pickle file path
            output_dir_path: converted kitti format file directory
            spd_path: path to SPD dataset
    """
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    with open(input_file_path, 'rb') as load_f:
        det_result_data = pickle.load(load_f)

    veh_frame = det_result_data["veh_id"]
    lidar2camera_path = f'{spd_path}/vehicle-side/calib/lidar_to_camera/{veh_frame}.json'
    camera2image_path = f'{spd_path}/vehicle-side/calib/camera_intrinsic/{veh_frame}.json'
    rotation, translation = get_lidar2camera(lidar2camera_path)
    calib_intrinsic = get_cam_calib_intrinsic(camera2image_path)
    output_file_path = output_dir_path + '/' + veh_frame + '.txt'
    if os.path.exists(output_file_path):
        print("veh_frame", veh_frame, "det_result_name", input_file_path.split('/')[-1].split('.')[0])
        save_file = open(output_file_path, 'a')
    else:
        save_file = open(output_file_path, 'w')
    num_boxes = len(det_result_data["labels_3d"].tolist())
    for i in range(num_boxes):
        lidar_3d_8points_det_result = det_result_data["boxes_3d"][i].tolist()
        lidar_3d_8points = [lidar_3d_8points_det_result[3], lidar_3d_8points_det_result[0], lidar_3d_8points_det_result[4],
                            lidar_3d_8points_det_result[7], lidar_3d_8points_det_result[2], lidar_3d_8points_det_result[1],
                            lidar_3d_8points_det_result[5], lidar_3d_8points_det_result[6]]

        # calculate l, w, h, x, y, z in LiDAR coordinate system
        lidar_xy0, lidar_xy3, lidar_xy1 = lidar_3d_8points[0][0:2], lidar_3d_8points[3][0:2], lidar_3d_8points[1][0:2]
        lidar_z4, lidar_z0 = lidar_3d_8points[4][2], lidar_3d_8points[0][2]
        l = math.sqrt((lidar_xy0[0] - lidar_xy3[0]) ** 2 + (lidar_xy0[1] - lidar_xy3[1]) ** 2)
        w = math.sqrt((lidar_xy0[0] - lidar_xy1[0]) ** 2 + (lidar_xy0[1] - lidar_xy1[1]) ** 2)
        h = lidar_z4 - lidar_z0
        lidar_x0, lidar_y0 = lidar_3d_8points[0][0], lidar_3d_8points[0][1]
        lidar_x2, lidar_y2 = lidar_3d_8points[2][0], lidar_3d_8points[2][1]
        lidar_x = (lidar_x0 + lidar_x2) / 2
        lidar_y = (lidar_y0 + lidar_y2) / 2
        lidar_z = (lidar_z0 + lidar_z4) / 2

        obj_type = id2type[det_result_data["labels_3d"][i]]
        score = det_result_data["scores_3d"][i]

        camera_3d_8points = []
        for lidar_point in lidar_3d_8points:
            camera_point = trans_point(lidar_point, rotation, translation)
            camera_3d_8points.append(camera_point)

        # generate the yaw angle of the object in the lidar coordinate system at the vehicle-side.
        lidar_rotation = get_label_lidar_rotation(lidar_3d_8points)
        # generate the alpha and yaw angle of the object in the camera coordinate system at the vehicle-side
        camera_x0, camera_z0 = camera_3d_8points[0][0], camera_3d_8points[0][2]
        camera_x2, camera_z2 = camera_3d_8points[2][0], camera_3d_8points[2][2]
        camera_x = (camera_x0 + camera_x2) / 2
        camera_y = camera_3d_8points[0][1]
        camera_z = (camera_z0 + camera_z2) / 2
        camera_3d_location = [camera_x, camera_y, camera_z]

        image_8points_2d = trans_points_cam2img(camera_3d_8points, calib_intrinsic)
        x_max = max(image_8points_2d[:][0])
        x_min = min(image_8points_2d[:][0])
        y_max = max(image_8points_2d[:][1])
        y_min = min(image_8points_2d[:][1])

        alpha, camera_rotation = get_camera_3d_alpha_rotation(camera_3d_8points, camera_3d_location)

        str_item = str(veh_frame) + ' ' + str(obj_type) + ' ' + '-1' + ' ' + '-1' + ' ' + '-1' + ' ' + str(alpha) + ' ' + str(
            x_min) + ' ' + str(y_min) + ' ' + str(x_max) + ' ' + str(y_max) + ' ' + str(h) + ' ' + str(w) + ' ' + str(l) + ' ' + str(
            camera_x) + ' ' + str(camera_y) + ' ' + str(camera_z) + ' ' + str(camera_rotation) + ' ' + str(lidar_x) + ' ' + str(
            lidar_y) + ' ' + str(lidar_z) + ' ' + str(lidar_rotation) + ' ' + '-1' + ' ' + str(score) + ' ' + '-1' + ' ' + '-1' + '\n'
        save_file.writelines(str_item)
    save_file.close()


def gen_kitti_result(input_dir_path, output_dir_path, spd_path):
    """
        Convert detection results from mmdetection3d_kitti format to KITTI format for all files in input_dir_path.
        Args:
            input_dir_path: directory containing mmdetection3d_kitti results pickle files
            output_dir_path: directory to save converted KITTI format files
            spd_path: path to SPD dataset
    """
    if os.path.exists(output_dir_path):
        os.system('rm -rf %s' % output_dir_path)
    os.makedirs(output_dir_path)
    for file in tqdm(os.listdir(input_dir_path)):
        path_file = input_dir_path + '/' + file
        label_det_result2kitti(path_file, output_dir_path, spd_path)


def gen_kitti_seq_result(input_dir_path, output_dir_path, spd_path):
    """
        Convert detection results from mmdetection3d_kitti format to KITTI format and group them by sequence.
        Args:
            input_dir_path: directory containing mmdetection3d_kitti results pickle files
            output_dir_path: directory to save converted KITTI format files grouped by sequence
            spd_path: path to SPD dataset
    """
    data_info = read_json(f'{spd_path}/vehicle-side/data_info.json')
    list_input_files = os.listdir(input_dir_path)
    if os.path.exists(output_dir_path):
        os.system('rm -rf %s' % output_dir_path)
    os.makedirs(output_dir_path)
    for input_file in tqdm(list_input_files):
        input_file_path = input_dir_path + '/' + input_file
        sequence_id = get_sequence_id(input_file.split('.')[0], data_info)
        sequence_path = output_dir_path + '/' + sequence_id
        if not os.path.exists(sequence_path):
            os.makedirs(sequence_path)
        os.system('cp %s %s/' % (input_file_path, sequence_path))


def gen_kitti_seq_txt(input_dir_path, output_dir_path):
    """
        Group converted KITTI format files by sequence and write them into one txt file per sequence.
        Args:
            input_dir_path: directory containing KITTI format files grouped by sequence
            output_dir_path: directory to save txt files grouped by sequence
    """
    if os.path.exists(output_dir_path):
        os.system('rm -rf %s' % output_dir_path)
    os.makedirs(output_dir_path)
    list_dir_sequences = os.listdir(input_dir_path)
    for dir_sequence in tqdm(list_dir_sequences):
        path_seq_input = input_dir_path + '/' + dir_sequence
        file_output = output_dir_path + '/' + dir_sequence + '.txt'
        save_file = open(file_output, 'w')
        list_files = os.listdir(path_seq_input)
        list_files.sort()
        for file in list_files:
            path_file = path_seq_input + '/' + file
            with open(path_file, "r") as read_f:
                data_txt = read_f.readlines()
                for item in data_txt:
                    save_file.writelines(item)
        save_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert detection results to KITTI format')
    parser.add_argument('--input-dir-path', type=str, required=True, help='Directory containing mmdetection3d_kitti results pickle files')
    parser.add_argument('--output-dir-path', type=str, required=True, help='Directory to save converted KITTI format files')
    parser.add_argument('--spd-path', type=str, required=True, help='Path to SPD dataset')
    args = parser.parse_args()

    input_dir_path = args.input_dir_path
    spd_path = args.spd_path

    output_dir_path = os.path.join(args.output_dir_path, 'label')
    output_dir_path_seq = os.path.join(args.output_dir_path, 'label_seq')
    output_dir_path_track = os.path.join(args.output_dir_path + 'label_track')
    # Convert detection results from mmdetection3d_kitti format to KITTI format for all files in input_dir_path
    gen_kitti_result(input_dir_path, output_dir_path, spd_path)
    # Group converted KITTI format files by sequence
    gen_kitti_seq_result(output_dir_path, output_dir_path_seq, spd_path)
    # Group converted KITTI format files by sequence and write them into one txt file per sequence
    gen_kitti_seq_txt(output_dir_path_seq, output_dir_path_track)

    os.system("cp %s/* %s/"%(output_dir_path_track,args.output_dir_path))
    os.system("rm -rf %s"%(output_dir_path))
    os.system("rm -rf %s"%(output_dir_path_seq))
    os.system("rm -rf %s"%(output_dir_path_track))
