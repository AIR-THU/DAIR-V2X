import os
from tools.dataset_converter.utils import read_json, get_lidar2camera, trans_point, get_lidar_3d_8points, get_camera_3d_alpha_rotation
from rich.progress import track


def concat_txt(input_path, output_path, output_file_name):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    path_file_output = output_path + '/' + output_file_name + '.txt'
    write_f = open(path_file_output, 'w')
    list_files = os.listdir(input_path)
    list_files.sort()
    for file in list_files:
        path_file_input = input_path + '/' + file
        with open(path_file_input, 'r') as read_f:
            list_lines = read_f.readlines()
            for line in list_lines:
                write_f.writelines(line)
    write_f.close()


def label_dair2kiiti_by_frame(dair_label_file_path, kitti_label_file_path, rotation, translation, frame, pointcloud_timestamp, no_classmerge):
    save_file = open(kitti_label_file_path, 'w')
    list_labels = read_json(dair_label_file_path)
    for label in list_labels:
        if not no_classmerge:
            label["type"] = label["type"].replace("Truck", "Car")
            label["type"] = label["type"].replace("Van", "Car")
            label["type"] = label["type"].replace("Bus", "Car")
        label_3d_dimensions = [float(label["3d_dimensions"]["l"]), float(label["3d_dimensions"]["w"]),
                               float(label["3d_dimensions"]["h"])]
        lidar_3d_location = [float(label["3d_location"]["x"]), float(label["3d_location"]["y"]),
                             float(label["3d_location"]["z"])]
        rotation_z = float(label["rotation"])
        lidar_3d_8_points = get_lidar_3d_8points(label_3d_dimensions, lidar_3d_location, rotation_z)

        lidar_3d_bottom_location = [float(label["3d_location"]["x"]), float(label["3d_location"]["y"]),
                                    float(label["3d_location"]["z"]) - float(label["3d_dimensions"]["h"]) / 2]
        camera_3d_location = trans_point(lidar_3d_bottom_location, rotation, translation)
        camera_3d_8_points = []
        for lidar_point in lidar_3d_8_points:
            camera_point = trans_point(lidar_point, rotation, translation)
            camera_3d_8_points.append(camera_point)

        alpha, rotation_y = get_camera_3d_alpha_rotation(camera_3d_8_points, camera_3d_location)

        list_item = [frame, str(label["type"]), str(label["track_id"]),
                     str(label["truncated_state"]), str(label["occluded_state"]), str(alpha),
                     str(label["2d_box"]["xmin"]), str(label["2d_box"]["ymin"]),
                     str(label["2d_box"]["xmax"]), str(label["2d_box"]["ymax"]), str(label_3d_dimensions[2]),
                     str(label_3d_dimensions[1]), str(label_3d_dimensions[0]), str(camera_3d_location[0]),
                     str(camera_3d_location[1]), str(camera_3d_location[2]), str(rotation_y), str(lidar_3d_location[0]),
                     str(lidar_3d_location[1]), str(lidar_3d_location[2]), str(rotation_z), pointcloud_timestamp, "1", "1",
                     str(label["token"])]
        str_item = ' '.join(list_item) + '\n'
        save_file.writelines(str_item)
    save_file.close()


def label_dair2kitti(source_root, target_root, temp_root, dict_sequence2tvt, frame_info, label_type, sensor_view, no_classmerge):
    if (sensor_view == "vehicle") or (sensor_view == "cooperative"):
        key_calib_l2c_path = "calib_lidar_to_camera_path"
    else:
        key_calib_l2c_path = "calib_virtuallidar_to_camera_path"
    for i in track(frame_info):
        calib_l2c_path = i[key_calib_l2c_path]
        calib_lidar_to_camera_path = f'{source_root}/{calib_l2c_path}'
        rotation, translation = get_lidar2camera(calib_lidar_to_camera_path)
        label_std_path = i["label_" + label_type + "_std_path"]
        source_label_path = f'{source_root}/{label_std_path}'
        temp_label_path = f'{temp_root}/{dict_sequence2tvt[i["sequence_id"]]}/{i["sequence_id"]}/label_02_split'
        if not os.path.exists(temp_label_path):
            os.makedirs(temp_label_path)
        temp_label_file_path = f'{temp_label_path}/{i["frame_id"]}.txt'
        label_dair2kiiti_by_frame(source_label_path, temp_label_file_path, rotation, translation, i["frame_id"], i["pointcloud_timestamp"], no_classmerge)

    list_tvt = os.listdir(temp_root)
    for tvt in list_tvt:
        temp_tvt_path = f'{temp_root}/{tvt}'
        list_seqs = os.listdir(temp_tvt_path)
        for seq in list_seqs:
            temp_label_path = f'{temp_tvt_path}/{seq}/label_02_split'
            target_label_path = f'{target_root}/{tvt}/{seq}/label_02'
            concat_txt(temp_label_path, target_label_path, seq)
