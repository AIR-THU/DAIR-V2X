import os
import argparse
from tools.dataset_converter.utils import read_json, get_lidar2camera, trans_point, get_lidar_3d_8points, get_camera_3d_alpha_rotation
from rich.progress import track

parser = argparse.ArgumentParser("Generate the Kitti Format Data")
parser.add_argument("--source-root", type=str, default="data/V2X-Seq-SPD",
                    help="Raw data root about SPD")
parser.add_argument("--target-root", type=str, default="data/KITTI-Track/cooperative",
                    help="The data root where the data with kitti-Track format is generated")
parser.add_argument("--split-path", type=str, default="data/split_datas/cooperative-split-data-spd.json",
                    help="Json file to split the data into training/validation/testing.")
parser.add_argument("--no-classmerge", action="store_true",
                    help="Not to merge the four classes [Car, Truck, Van, Bus] into one class [Car]")
parser.add_argument("--temp-root", type=str, default="./tmp_file", help="Temporary intermediate file root.")


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


def label_dair2kiiti_by_frame(dair_label_file_path, kitti_label_file_path, rotation, translation, frame, pointcloud_timestamp,
                              no_classmerge):
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


def label_dair2kitti(source_root, target_root, temp_root, dict_sequence2tvt, frame_info, no_classmerge):
    for i in track(frame_info):
        calib_lidar_to_camera_path = f'{source_root}/vehicle-side/calib/lidar_to_camera/{i["vehicle_frame"]}.json'
        rotation, translation = get_lidar2camera(calib_lidar_to_camera_path)
        source_label_path = f'{source_root}/cooperative/label/{i["vehicle_frame"]}.json'
        temp_label_path = f'{temp_root}/{dict_sequence2tvt[i["vehicle_sequence"]]}/{i["vehicle_sequence"]}/label_02_split'
        os.makedirs(temp_label_path, exist_ok=True)
        temp_label_file_path = f'{temp_label_path}/{i["vehicle_frame"]}.txt'
        label_dair2kiiti_by_frame(source_label_path, temp_label_file_path, rotation, translation, i["vehicle_frame"], "-1", no_classmerge)

    list_tvt = os.listdir(temp_root)
    for tvt in list_tvt:
        temp_tvt_path = f'{temp_root}/{tvt}'
        list_seqs = os.listdir(temp_tvt_path)
        for seq in list_seqs:
            temp_label_path = f'{temp_tvt_path}/{seq}/label_02_split'
            target_label_path = f'{target_root}/{tvt}/{seq}/label_02'
            concat_txt(temp_label_path, target_label_path, seq)


if __name__ == "__main__":
    args = parser.parse_args()
    spd_data_root = args.source_root
    target_root = args.target_root
    split_path = args.split_path
    split_info = read_json(split_path)
    dict_sequence2tvt = {}
    for tvt in [["train", "training"], ["val", "validation"], ["test", "testing"]]:
        for seq in split_info["batch_split"][tvt[0]]:
            dict_sequence2tvt[seq] = tvt[1]
    frame_info = read_json(f'{spd_data_root}/cooperative/data_info.json')
    temp_root = args.temp_root
    no_classmerge = args.no_classmerge
    if os.path.exists(temp_root):
        os.system("rm -rf %s" % temp_root)
    os.system("mkdir -p %s" % temp_root)
    label_dair2kitti(spd_data_root, target_root, temp_root, dict_sequence2tvt, frame_info, no_classmerge)
    os.system("cp -r %s/* %s/" % (temp_root, target_root))
    os.system("rm -rf %s" % temp_root)
