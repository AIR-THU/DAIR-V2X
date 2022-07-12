import os
import os.path as osp
from abc import ABC, abstractmethod
import torch

from dataset.dataset_utils import read_pcd, read_jpg, load_json
from v2x_utils.transformation_utils import Coord_transformation
from v2x_utils import get_trans, box_translation
import json
import numpy as np


class Frame(dict, ABC):
    def __init__(self, path, info_dict):
        self.path = path
        for key in info_dict:
            self.__setitem__(key, info_dict[key])

    @abstractmethod
    def point_cloud(self, **args):
        raise NotImplementedError

    @abstractmethod
    def image(self, **args):
        raise NotImplementedError


class VehFrame(Frame):
    def __init__(self, path, veh_dict, tmp_key="tmps"):
        super().__init__(path, veh_dict)
        self.id = {}
        self.id["lidar"] = veh_dict["pointcloud_path"][-10:-4]
        self.id["camera"] = veh_dict["image_path"][-10:-4]
        self.tmp = "../cache/" + tmp_key + "/tmp_v_" + self.id["lidar"] + ".bin"
        if not osp.exists("../cache/" + tmp_key):
            os.system("mkdir -p ../cache/" + tmp_key)

    def point_cloud(self, data_format="array"):
        points, _ = read_pcd(osp.join(self.path, self.get("pointcloud_path")))
        if data_format == "array":
            return points, _
        elif data_format == "file":
            if not osp.exists(self.tmp):
                points.tofile(self.tmp)
            return self.tmp
        elif data_format == "tensor":
            return torch.tensor(points)

    def image(self, data_format="rgb"):
        image_array = read_jpg(osp.join(self.path, self.get("image_path")))
        if data_format == "array":
            return image_array
        elif data_format == "file":
            if not osp.exists(self.tmp):
                image_array.tofile(self.tmp)
            return self.tmp
        elif data_format == "tensor":
            return torch.tensor(image_array)


class InfFrame(Frame):
    def __init__(self, path, inf_dict, tmp_key="tmps"):
        super().__init__(path, inf_dict)
        self.id = {}
        self.id["lidar"] = inf_dict["pointcloud_path"][-10:-4]
        self.id["camera"] = inf_dict["image_path"][-10:-4]
        self.tmp = "../cache/" + tmp_key + "/tmp_i_" + self.id["lidar"] + ".bin"
        if not osp.exists("../cache/" + tmp_key):
            os.system("mkdir ../cache/" + tmp_key)

    def point_cloud(self, data_format="array"):
        points, _ = read_pcd(osp.join(self.path, self.get("pointcloud_path")))
        if data_format == "array":
            return points, _
        elif data_format == "file":
            if not osp.exists(self.tmp):
                points.tofile(self.tmp)
            return self.tmp
        elif data_format == "tensor":
            return torch.tensor(points)

    def image(self, data_format="rgb"):
        image_array = read_jpg(osp.join(self.path, self.get("image_path")))
        if data_format == "array":
            return image_array
        elif data_format == "file":
            if not osp.exists(self.tmp):
                image_array.copy(self.tmp)
            return self.tmp
        elif data_format == "tensor":
            return torch.tensor(image_array)

    def transform(self, from_coord="", to_coord=""):
        """
        This function serves to calculate the Transformation Matrix from 'from_coord' to 'to_coord'
        coord_list=['Infrastructure_image','Infrastructure_camera','Infrastructure_lidar',
                       'world', 'Vehicle_image','Vehicle_camera','Vehicle_lidar',
                       'Vehicle_novatel']
        Args:
            from_coord(str): element in the coord_list
            to_coord(str):  element in coord_list
        Return:
            Transformation_Matrix: Transformation Matrix from 'from_coord' to 'to_coord'
        """
        infra_name = self.id["camera"]
        trans = Coord_transformation(from_coord, to_coord, "/".join(self.path.split("/")[:-2]), infra_name, "")
        return trans


class VICFrame(Frame):
    def __init__(self, path, info_dict, veh_frame, inf_frame, time_diff, offset=None):
        # TODO: build vehicle frame and infrastructure frame
        super().__init__(path, info_dict)
        self.veh_frame = veh_frame
        self.inf_frame = inf_frame
        self.time_diff = time_diff
        self.transformation = None
        if offset is None:
            offset = load_json(osp.join(self.inf_frame.path, self.inf_frame["calib_virtuallidar_to_world_path"]))[
                "relative_error"
            ]
        self.offset = offset

    def vehicle_frame(self):
        return self.veh_frame

    def infrastructure_frame(self):
        return self.inf_frame

    def proc_transformation(self):
        # self.transformation["infrastructure_image"]["world"]
        # read vehicle to world
        # read infrastructure to novaltel
        # read novaltel to world
        # compute inv
        # compose
        pass

    def transform(self, from_coord="", to_coord=""):
        """
        This function serves to calculate the Transformation Matrix from 'from_coord' to 'to_coord'
        coord_list=['Infrastructure_image','Infrastructure_camera','Infrastructure_lidar',
                       'world', 'Vehicle_image','Vehicle_camera','Vehicle_lidar',
                       'Vehicle_novatel']
        Args:
            from_coord(str): element in the coord_list
            to_coord(str):  element in coord_list
        Return:
            Transformation_Matrix: Transformation Matrix from 'from_coord' to 'to_coord'
        """
        veh_name = self.veh_frame["image_path"][-10:-4]
        infra_name = self.inf_frame["image_path"][-10:-4]
        trans = Coord_transformation(from_coord, to_coord, self.path, infra_name, veh_name)
        return trans
