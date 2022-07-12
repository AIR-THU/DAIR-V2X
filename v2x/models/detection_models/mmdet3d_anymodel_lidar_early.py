import os.path as osp
import sys
import os
import numpy as np
import torch.nn as nn
import logging

logger = logging.getLogger(__name__)

from base_model import BaseModel
from model_utils import (
    init_model,
    inference_detector,
    inference_mono_3d_detector,
    BBoxList,
    EuclidianMatcher,
    SpaceCompensator,
    TimeCompensator,
    BasicFuser,
    read_pcd,
    concatenate_pcd2bin,
)
from dataset.dataset_utils import (
    load_json,
    save_pkl,
    load_pkl,
    read_jpg,
)
from v2x_utils import (
    mkdir,
    get_arrow_end,
    box_translation,
    points_translation,
    get_trans,
    diff_label_filt,
)


def get_box_info(result):
    if len(result[0]["boxes_3d"].tensor) == 0:
        box_lidar = np.zeros((1, 8, 3))
        box_ry = np.zeros(1)
    else:
        box_lidar = result[0]["boxes_3d"].corners.numpy()
        box_ry = result[0]["boxes_3d"].tensor[:, -1].numpy()
    box_centers_lidar = box_lidar.mean(axis=1)
    arrow_ends_lidar = get_arrow_end(box_centers_lidar, box_ry)
    return box_lidar, box_ry, box_centers_lidar, arrow_ends_lidar


def gen_pred_dict(id, timestamp, box, arrow, points, score, label):
    if len(label) == 0:
        score = [-2333]
        label = [-1]
    save_dict = {
        "info": id,
        "timestamp": timestamp,
        "boxes_3d": box.tolist(),
        "arrows": arrow.tolist(),
        "scores_3d": score,
        "labels_3d": label,
        "points": points.tolist(),
    }
    return save_dict


class EarlyFusion(BaseModel):
    def add_arguments(parser):
        parser.add_argument("--inf-config-path", type=str, default="")
        parser.add_argument("--inf-model-path", type=str, default="")
        parser.add_argument("--veh-config-path", type=str, default="")
        parser.add_argument("--veh-model-path", type=str, default="")
        parser.add_argument("--no-comp", action="store_true")
        parser.add_argument("--overwrite-cache", action="store_true")

    def __init__(self, args, pipe):
        super().__init__()
        self.model = LateFusionVeh(args)
        self.args = args
        self.pipe = pipe
        mkdir(args.output)
        mkdir(osp.join(args.output, "inf"))
        mkdir(osp.join(args.output, "veh"))
        mkdir(osp.join(args.output, "inf", "lidar"))
        mkdir(osp.join(args.output, "veh", "lidar"))
        mkdir(osp.join(args.output, "inf", "camera"))
        mkdir(osp.join(args.output, "veh", "camera"))
        mkdir(osp.join(args.output, "result"))

    def forward(self, vic_frame, filt, prev_inf_frame_func=None, *args):
        save_path = osp.join(vic_frame.path, "vehicle-side", "cache")
        if not osp.exists(save_path):
            mkdir(save_path)
        name = vic_frame.veh_frame["image_path"][-10:-4]
        Inf_points = read_pcd(osp.join(vic_frame.path, "infrastructure-side", vic_frame.inf_frame["pointcloud_path"]))
        Veh_points = read_pcd(osp.join(vic_frame.path, "vehicle-side", vic_frame.veh_frame["pointcloud_path"]))
        vic_frame_trans = vic_frame.transform(from_coord="Infrastructure_lidar", to_coord="Vehicle_lidar")
        for i in range(len(Inf_points.pc_data)):
            temp = vic_frame_trans.single_point_transformation(
                [Inf_points.pc_data[i][0], Inf_points.pc_data[i][1], Inf_points.pc_data[i][2]]
            )
            for j in range(3):
                Inf_points.pc_data[i][j] = temp[j]
            Inf_points.pc_data[i][3] = Inf_points.pc_data[i][3] * 255
        concatenate_pcd2bin(Inf_points, Veh_points, osp.join(save_path, name + ".pcd"))
        vic_frame.veh_frame["pointcloud_path"] = osp.join("cache", name + ".pcd")
        pred, id_veh = self.model(vic_frame.vehicle_frame(), None, filt)

        # Hard Code to change the prediction label
        for ii in range(len(pred["labels_3d"])):
            pred["labels_3d"][ii] = 2

        self.pipe.send("boxes_3d", pred["boxes_3d"])
        self.pipe.send("labels_3d", pred["labels_3d"])
        self.pipe.send("scores_3d", pred["scores_3d"])

        return {
            "boxes_3d": np.array(pred["boxes_3d"]),
            "labels_3d": np.array(pred["labels_3d"]),
            "scores_3d": np.array(pred["scores_3d"]),
        }


class LateFusionVeh(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.model = None
        self.args = args
        self.args.overwrite_cache = True

    def pred(self, frame, trans, pred_filter):
        if self.args.sensortype == "lidar":
            id = frame.id["lidar"]
            logger.debug("vehicle pointcloud_id: {}".format(id))
            path = osp.join(self.args.output, "veh", "lidar", id + ".pkl")
            frame_timestamp = frame["pointcloud_timestamp"]

            if osp.exists(path) and self.args.overwrite_cache:
                pred_dict = load_pkl(path)
                return pred_dict, id

            logger.debug("predicting...")
            if self.model is None:
                raise Exception

            tmp = frame.point_cloud(data_format="file")
            result, _ = inference_detector(self.model, tmp)
            box, box_ry, box_center, arrow_ends = get_box_info(result)
            if trans is not None:
                box = trans(box)  #
                box_center = trans(box_center)[:, np.newaxis, :]
                arrow_ends = trans(arrow_ends)[:, np.newaxis, :]

            remain = []
            if len(result[0]["boxes_3d"].tensor) != 0:
                for i in range(box.shape[0]):
                    if pred_filter(box[i]):
                        remain.append(i)

            if len(remain) >= 1:
                box = box[remain]
                box_center = box_center[remain]
                arrow_ends = arrow_ends[remain]
                result[0]["scores_3d"] = result[0]["scores_3d"].numpy()[remain]
                result[0]["labels_3d"] = result[0]["labels_3d"].numpy()[remain]
            else:
                box = np.zeros((1, 8, 3))
                box_center = np.zeros((1, 1, 3))
                arrow_ends = np.zeros((1, 1, 3))
                result[0]["labels_3d"] = np.zeros((1))
                result[0]["scores_3d"] = np.zeros((1))

            if self.args.save_point_cloud:
                save_data = frame.point_cloud(format="array")
            else:
                save_data = np.array([])

            pred_dict = gen_pred_dict(
                id,
                frame_timestamp,
                box,
                np.concatenate([box_center, arrow_ends], axis=1),
                save_data,
                result[0]["scores_3d"].tolist(),
                result[0]["labels_3d"].tolist(),
            )
            save_pkl(pred_dict, path)

            return pred_dict, id
        else:
            print("Now early fusion only supports LiDAR sensor!")
            raise Exception

    def forward(self, data, trans, pred_filter):
        try:
            pred_dict, id = self.pred(data, trans, pred_filter)
        except Exception:
            logger.info("building model")
            self.model = init_model(
                self.args.veh_config_path,
                self.args.veh_model_path,
                device=self.args.device,
            )
            pred_dict, id = self.pred(data, trans, pred_filter)

        return pred_dict, id


if __name__ == "__main__":
    sys.path.append("..")
    sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])
