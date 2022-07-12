import os
import json
from tqdm import tqdm
import argparse
import errno


def read_json(path_json):
    with open(path_json, "r") as load_f:
        my_json = json.load(load_f)
    return my_json


def write_json(path_json, new_dict):
    with open(path_json, "w") as f:
        json.dump(new_dict, f)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_data(data_info, path_pcd):
    for data in data_info:
        name1 = os.path.split(path_pcd)[-1]
        name2 = os.path.split(data["pointcloud_path"])[-1]
        if name1 == name2:
            return data


def choose_name(name_list, path_v_data_info):
    v_data_info = read_json(path_v_data_info)
    fusion_data_info = []
    for i in tqdm(range(len(name_list))):
        data = get_data(v_data_info, name_list[i])
        fusion_data_info.append(data)
    return fusion_data_info


def get_name(path_c_data_info):
    c_data_info = read_json(path_c_data_info)
    name_list = []
    for data in c_data_info:
        name = os.path.split(data["vehicle_pointcloud_path"])[-1]
        name_list.append(name)
    return name_list


def get_fusion_label(path_c, path_dest):
    path_c_data_info = os.path.join(path_c, "cooperative/data_info.json")
    path_v_data_info = os.path.join(path_c, "vehicle-side/data_info.json")
    name_list = get_name(path_c_data_info)
    fusion_data_info = choose_name(name_list, path_v_data_info)
    write_json(os.path.join(path_dest, "fusion_data_info.json"), fusion_data_info)


parser = argparse.ArgumentParser("Generate cooperative-vehicle data info.")
parser.add_argument(
    "--source-root",
    type=str,
    default="./data/cooperative-vehicle-infrastructure",
    help="Raw data root about DAIR-V2X-C.",
)
parser.add_argument(
    "--target-root",
    type=str,
    default="./data_info-fusioned",
    help="The fusioned data info",
)

if __name__ == "__main__":
    args = parser.parse_args()
    source_root = args.source_root
    target_label_root = args.target_root
    get_fusion_label(source_root, target_label_root)
