import argparse
import os
from tools.dataset_converter.spd2kitti_detection.gen_kitti.label_dair2kitti import label_dair2kitti
from tools.dataset_converter.spd2kitti_detection.gen_kitti.calib_dair2kitti import gen_calib2kitti
from tools.dataset_converter.spd2kitti_detection.gen_kitti.gen_ImageSets_from_split_data import gen_ImageSet
from tools.dataset_converter.utils import read_json, pcd2bin
from rich.progress import track

parser = argparse.ArgumentParser("Generate the Kitti Format Data")
parser.add_argument("--source-root", type=str, default="data/SPD/cooperative-vehicle-infrastructure/vehicle-side",
                    help="Raw data root about SPD")
parser.add_argument("--target-root", type=str, default="data/KITTI/cooperative-vehicle-infrastructure/vehicle-side",
                    help="The data root where the data with kitti format is generated")
parser.add_argument("--split-path", type=str, default="data/split_datas/cooperative-split-data-spd.json",
                    help="Json file to split the data into training/validation/testing.")
parser.add_argument("--label-type", type=str, default="lidar", help="label type from ['lidar', 'camera']")
parser.add_argument("--sensor-view", type=str, default="vehicle", help="Sensor view from ['infrastructure', 'vehicle']")
parser.add_argument("--no-classmerge", action="store_true",
                    help="Not to merge the four classes [Car, Truck, Van, Bus] into one class [Car]")
parser.add_argument("--temp-root", type=str, default="./tmp_file", help="Temporary intermediate file root.")


def rawdata_copy(source_root, target_root, dict_sequence2tvt, frame_info):
    for i in track(frame_info):
        # copy image
        source_image_path = f'{source_root}/{i["image_path"]}'
        target_image_path = f'{target_root}/{dict_sequence2tvt[i["sequence_id"]]}/image_2'
        if not os.path.exists(target_image_path):
            os.makedirs(target_image_path)
        os.system("cp %s %s/" % (source_image_path, target_image_path))
        # copy point cloud
        source_velodyne_pcd_path = f'{source_root}/{i["pointcloud_path"]}'
        source_velodyne_bin_path = source_velodyne_pcd_path.replace(".pcd", ".bin")
        target_velodyne_path = f'{target_root}/{dict_sequence2tvt[i["sequence_id"]]}/velodyne'
        if not os.path.exists(target_velodyne_path):
            os.makedirs(target_velodyne_path)
        if not os.path.exists(source_velodyne_bin_path):
            pcd2bin(source_velodyne_pcd_path, f'{target_velodyne_path}/{i["frame_id"]}.bin')
        else:
            os.system("cp %s %s/" % (source_velodyne_bin_path, target_velodyne_path))


if __name__ == "__main__":
    print("================ Start to Convert ================")
    args = parser.parse_args()
    source_root = args.source_root
    target_root = args.target_root
    split_path = args.split_path
    split_info = read_json(split_path)
    dict_sequence2tvt = {}
    for tvt in [["train", "training"], ["val", "training"], ["test", "testing"]]:
        for seq in split_info["batch_split"][tvt[0]]:
            dict_sequence2tvt[seq] = tvt[1]
    frame_info = read_json(f'{source_root}/data_info.json')

    print("================ Start to Copy Raw Data ================")
    rawdata_copy(source_root, target_root, dict_sequence2tvt, frame_info)

    print("================ Start to Generate Label ================")
    temp_root = args.temp_root
    label_type = args.label_type
    sensor_view = args.sensor_view
    no_classmerge = args.no_classmerge
    if os.path.exists(temp_root):
        os.system("rm -rf %s" % temp_root)
    os.system("mkdir -p %s" % temp_root)
    label_dair2kitti(source_root, temp_root, dict_sequence2tvt, frame_info, label_type, sensor_view, no_classmerge)
    os.system("cp -r %s/* %s/" % (temp_root, target_root))
    os.system("rm -rf %s" % temp_root)

    print("================ Start to Generate Calibration Files ================")
    gen_calib2kitti(source_root, target_root, dict_sequence2tvt, sensor_view)

    print("================ Start to Generate ImageSet Files ================")
    gen_ImageSet(target_root, split_info, sensor_view)
