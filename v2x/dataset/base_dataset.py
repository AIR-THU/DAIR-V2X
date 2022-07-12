import os.path as osp
import json
import os

from torch.utils.data import Dataset
from v2x_utils import get_trans
from dataset.dataset_utils import load_json


def get_annos(path, prefix, single_frame, sensortype="camera"):
    img_path = path + prefix + single_frame["image_path"]
    trans0_path = ""
    if "calib_lidar_to_camera_path" in single_frame.keys():
        trans0_path = single_frame["calib_lidar_to_camera_path"]
    else:
        trans0_path = single_frame["calib_virtuallidar_to_camera_path"]
    trans1_path = single_frame["calib_camera_intrinsic_path"]
    trans0, rot0 = get_trans(load_json(osp.join(path, prefix, trans0_path)))
    lidar2camera = {}
    lidar2camera.update(
        {
            "translation": trans0,
            "rotation": rot0,
        }
    )
    # trans0, rot0 = lidar2camera["translation"], lidar2camera["rotation"]
    camera2image = load_json(osp.join(path, prefix, trans1_path))["cam_K"]

    annFile = {}
    img_ann = {}
    calib = {}
    calib.update(
        {
            "cam_intrinsic": camera2image,
            "Tr_velo_to_cam": lidar2camera,
        }
    )

    img_ann.update({"file_name": img_path, "calib": calib})
    imglist = []
    imglist.append(img_ann)
    annFile.update({"images": imglist})
    if not osp.exists(osp.join(path, prefix, "annos")):
        os.mkdir(osp.join(path, prefix, "annos"))
    ann_path_o = osp.join(path, prefix, "annos", single_frame["image_path"].split("/")[-1].split(".")[0] + ".json")
    with open(ann_path_o, "w") as f:
        json.dump(annFile, f)


def build_path_to_info(prefix, data, sensortype="lidar"):
    path2info = {}
    if sensortype == "lidar":
        for elem in data:
            if elem["pointcloud_path"] == "":
                continue
            path = osp.join(prefix, elem["pointcloud_path"])
            path2info[path] = elem
    elif sensortype == "camera":
        for elem in data:
            if elem["image_path"] == "":
                continue
            path = osp.join(prefix, elem["image_path"])
            path2info[path] = elem
    return path2info


class DAIRV2XDataset(Dataset):
    def __init__(self, path, args, split="train", extended_range=None):
        super().__init__()

        self.split = None
