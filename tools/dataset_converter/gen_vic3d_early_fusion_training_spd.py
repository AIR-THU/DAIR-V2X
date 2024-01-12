import os
import json
import argparse
from tqdm import tqdm


parser = argparse.ArgumentParser("Generate the Early Fusion Data")
parser.add_argument("--source-root", type=str, default="data/V2X-Seq-SPD", help="Raw data root about SPD.")


def read_json(path_json):
    with open(path_json, "r") as load_f:
        my_json = json.load(load_f)
    return my_json


if __name__ == "__main__":
    args = parser.parse_args()
    source_root = args.source_root

    os.makedirs(f'{source_root}/vic3d-early-fusion-training/calib/camera_intrinsic', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/calib/lidar_to_camera', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/calib/lidar_to_novatel', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/calib/novatel_to_world', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/image', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/velodyne', exist_ok=True)
    os.makedirs(f'{source_root}/vic3d-early-fusion-training/label/lidar', exist_ok=True)

    coop_data_info = read_json(f"{source_root}/cooperative/data_info.json")
    for i in tqdm(coop_data_info):
        os.system("cp %s/vehicle-side/calib/camera_intrinsic/%s.json %s/vic3d-early-fusion-training/calib/camera_intrinsic/" % (source_root, i["vehicle_frame"], source_root))
        os.system("cp %s/vehicle-side/calib/lidar_to_camera/%s.json %s/vic3d-early-fusion-training/calib/lidar_to_camera/" % (source_root, i["vehicle_frame"], source_root))
        os.system("cp %s/vehicle-side/calib/lidar_to_novatel/%s.json %s/vic3d-early-fusion-training/calib/lidar_to_novatel/" % (source_root, i["vehicle_frame"], source_root))
        os.system("cp %s/vehicle-side/calib/novatel_to_world/%s.json %s/vic3d-early-fusion-training/calib/novatel_to_world/" % (source_root, i["vehicle_frame"], source_root))

        os.system("cp %s/vehicle-side/image/%s.jpg %s/vic3d-early-fusion-training/image/" % (source_root, i["vehicle_frame"], source_root))
        os.system("cp %s/cooperative/label/%s.json %s/vic3d-early-fusion-training/label/lidar/" % (source_root, i["vehicle_frame"], source_root))

        os.system("cp %s/vehicle-side/data_info.json %s/vic3d-early-fusion-training/" % (source_root, source_root))
