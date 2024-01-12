import argparse
import os
from tools.dataset_converter.gen_kitti.label_lidarcoord_to_cameracoord import gen_lidar2cam
from tools.dataset_converter.gen_kitti.label_json2kitti import json2kitti, rewrite_label, label_filter
from tools.dataset_converter.gen_kitti.gen_calib2kitti import gen_calib2kitti
from tools.dataset_converter.gen_kitti.gen_ImageSets_from_split_data import gen_ImageSet_from_split_data
from tools.dataset_converter.utils import pcd2bin

parser = argparse.ArgumentParser("Generate the Kitti Format Data")
parser.add_argument("--source-root", type=str, default="data/single-vehicle-side", help="Raw data root about DAIR-V2X.")
parser.add_argument(
    "--target-root",
    type=str,
    default="./single-vehicle-side-point-cloud-kitti",
    help="The data root where the data with kitti format is generated",
)
parser.add_argument(
    "--split-path",
    type=str,
    default="data/split_datas/single-vehicle-split-data.json",
    help="Json file to split the data into training/validation/testing.",
)
parser.add_argument("--label-type", type=str, default="lidar", help="label type from ['lidar', 'camera']")
parser.add_argument("--sensor-view", type=str, default="vehicle", help="Sensor view from ['infrastructure', 'vehicle']")
parser.add_argument(
    "--no-classmerge",
    action="store_true",
    help="Not to merge the four classes [Car, Truck, Van, Bus] into one class [Car]",
)
parser.add_argument("--temp-root", type=str, default="./tmp_file", help="Temporary intermediate file root.")


def mdkir_kitti(target_root):
    if not os.path.exists(target_root):
        os.makedirs(target_root)

    os.system("mkdir -p %s/training" % target_root)
    os.system("mkdir -p %s/training/calib" % target_root)
    os.system("mkdir -p %s/training/label_2" % target_root)
    os.system("mkdir -p %s/testing" % target_root)
    os.system("mkdir -p %s/ImageSets" % target_root)


def rawdata_copy(source_root, target_root):
    os.system("cp -r %s/image %s/training/image_2" % (source_root, target_root))
    os.system("cp -r %s/velodyne %s/training" % (source_root, target_root))


def kitti_pcd2bin(target_root):
    pcd_dir = os.path.join(target_root, "training/velodyne")
    fileList = os.listdir(pcd_dir)
    for fileName in fileList:
        if ".pcd" in fileName:
            pcd_file_path = pcd_dir + "/" + fileName
            bin_file_path = pcd_dir + "/" + fileName.replace(".pcd", ".bin")
            pcd2bin(pcd_file_path, bin_file_path)


if __name__ == "__main__":
    print("================ Start to Convert ================")
    args = parser.parse_args()
    source_root = args.source_root
    target_root = args.target_root

    print("================ Start to Copy Raw Data ================")
    mdkir_kitti(target_root)
    rawdata_copy(source_root, target_root)
    kitti_pcd2bin(target_root)

    print("================ Start to Generate Label ================")
    temp_root = args.temp_root
    label_type = args.label_type
    no_classmerge = args.no_classmerge
    os.system("mkdir -p %s" % temp_root)
    os.system("rm -rf %s/*" % temp_root)
    gen_lidar2cam(source_root, temp_root, label_type=label_type)

    json_root = os.path.join(temp_root, "label", label_type)
    kitti_label_root = os.path.join(target_root, "training/label_2")
    json2kitti(json_root, kitti_label_root)
    if not no_classmerge:
        rewrite_label(kitti_label_root)
    label_filter(kitti_label_root)

    os.system("rm -rf %s" % temp_root)

    print("================ Start to Generate Calibration Files ================")
    sensor_view = args.sensor_view
    path_camera_intrinsic = os.path.join(source_root, "calib/camera_intrinsic")
    if sensor_view == "vehicle" or sensor_view == "cooperative":
        path_lidar_to_camera = os.path.join(source_root, "calib/lidar_to_camera")
    else:
        path_lidar_to_camera = os.path.join(source_root, "calib/virtuallidar_to_camera")
    path_calib = os.path.join(target_root, "training/calib")
    gen_calib2kitti(path_camera_intrinsic, path_lidar_to_camera, path_calib)

    print("================ Start to Generate ImageSet Files ================")
    split_json_path = args.split_path
    ImageSets_path = os.path.join(target_root, "ImageSets")
    gen_ImageSet_from_split_data(ImageSets_path, split_json_path, sensor_view)
