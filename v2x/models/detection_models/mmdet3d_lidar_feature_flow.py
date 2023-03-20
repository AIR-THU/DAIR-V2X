import torch.nn as nn
import os.path as osp
import numpy as np
import torch.nn as nn
import logging
logger = logging.getLogger(__name__)
from tqdm import tqdm
from base_model import BaseModel
from pypcd import pypcd
import mmcv
import numpy as np
import re
import torch
from copy import deepcopy
from mmcv.parallel import collate, scatter
from mmcv.runner import load_checkpoint
from os import path as osp
from mmdet3d.core import (
    Box3DMode,
    CameraInstance3DBoxes,
    DepthInstance3DBoxes,
    LiDARInstance3DBoxes,
    show_multi_modality_result,
    show_result,
    show_seg_result,
)
from mmdet3d.core.bbox import get_box_type
from mmdet3d.datasets.pipelines import Compose
from mmdet3d.models import build_model
from model_utils import (
    init_model,
    inference_mono_3d_detector,
    BBoxList,
    EuclidianMatcher,
    SpaceCompensator,
    TimeCompensator,
    BasicFuser,
    read_pcd,
    concatenate_pcd2bin
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
    for i in range(len(result[0]["boxes_3d"])):
        temp=result[0]["boxes_3d"].tensor[i][4].clone()
        result[0]["boxes_3d"].tensor[i][4]=result[0]["boxes_3d"].tensor[i][3]
        result[0]["boxes_3d"].tensor[i][3]=temp
        result[0]["boxes_3d"].tensor[i][6]=result[0]["boxes_3d"].tensor[i][6]
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

def inference_detector_feature_fusion(model, veh_bin, inf_bin, rotation, translation, vic_frame):
    """Inference point cloud with the detector.
    Args:
        model (nn.Module): The loaded detector.
        pcd (str): Point cloud files.
    Returns:
        tuple: Predicted results and data from pipeline.
    """
    cfg = model.cfg
    device = next(model.parameters()).device  # model device
    # build the data pipeline
    test_pipeline = deepcopy(cfg.data.test.pipeline)
    test_pipeline = Compose(test_pipeline)
    box_type_3d, box_mode_3d = get_box_type(cfg.data.test.box_type_3d)
    data = dict(
        vehicle_pts_filename=veh_bin,
        infrastructure_pts_filename=inf_bin,
        box_type_3d=box_type_3d,
        box_mode_3d=box_mode_3d,
        # for ScanNet demo we need axis_align_matrix
        ann_info=dict(axis_align_matrix=np.eye(4)),
        sweeps=[],
        # set timestamp = 0
        timestamp=[0],
        img_fields=[],
        bbox3d_fields=[],
        pts_mask_fields=[],
        pts_seg_fields=[],
        bbox_fields=[],
        mask_fields=[],
        seg_fields=[],
    )
    data = test_pipeline(data)
    a=dict(
        rotation = rotation,
        translation = translation
    )

    data = collate([data], samples_per_gpu=1)
    if next(model.parameters()).is_cuda:
    # scatter to specified GPU
        data = scatter(data, [device.index])[0]
        data['img_metas'][0][0]['inf2veh']=a 
        data['img_metas'][0][0]['infrastructure_idx_t_1']=vic_frame['infrastructure_idx_t_1']
        data['img_metas'][0][0]['infrastructure_pointcloud_bin_path_t_1']=vic_frame['infrastructure_pointcloud_bin_path_t_1']
        data['img_metas'][0][0]['infrastructure_idx_t_0']=vic_frame['infrastructure_idx_t_0']
        data['img_metas'][0][0]['infrastructure_pointcloud_bin_path_t_0']=vic_frame['infrastructure_pointcloud_bin_path_t_0']
        data['img_metas'][0][0]['infrastructure_t_0_1']=vic_frame['infrastructure_t_0_1']
        data['img_metas'][0][0]['infrastructure_idx_t_2']=vic_frame['infrastructure_idx_t_2']
        data['img_metas'][0][0]['infrastructure_pointcloud_bin_path_t_2']=vic_frame['infrastructure_pointcloud_bin_path_t_2']
        data['img_metas'][0][0]['infrastructure_t_1_2']=vic_frame['infrastructure_t_1_2']
    else:
    # this is a workaround to avoid the bug of MMDataParallel
        data["img_metas"] = data["img_metas"][0].data
        data["points"] = data["points"][0].data
    # forward the model
    # print(data["img_metas"])
    with torch.no_grad():
        result = model(return_loss=False, rescale=True, **data)
    return result, data

class FeatureFlow(BaseModel):
    def add_arguments(parser):
        parser.add_argument("--inf-config-path", type=str, default="")
        parser.add_argument("--inf-model-path", type=str, default="")
        parser.add_argument("--veh-config-path", type=str, default="")
        parser.add_argument("--veh-model-path", type=str, default="")
        parser.add_argument("--no-comp", action="store_true")
        parser.add_argument("--overwrite-cache", action="store_true")

    def __init__(self, args,pipe):
        super().__init__()
        # self.model = LateFusionVeh(args)
        if osp.exists(args.output):
            import shutil
            shutil.rmtree(args.output)
        self.args = args
        self.pipe=pipe
        self.model = init_model(
                self.args.veh_config_path,
                self.args.veh_model_path,
                device=self.args.device,
         )
        # self.model.flownet_init()
        mkdir(args.output)
        mkdir(osp.join(args.output, "inf"))
        mkdir(osp.join(args.output, "veh"))
        mkdir(osp.join(args.output, "inf", "lidar"))
        mkdir(osp.join(args.output, "veh", "lidar"))
        mkdir(osp.join(args.output, "inf", "camera"))
        mkdir(osp.join(args.output, "veh", "camera"))
        mkdir(osp.join(args.output, "result"))

    def forward(self, vic_frame, filt, prev_inf_frame_func=None, *args):
        tmp_veh = vic_frame.veh_frame.point_cloud(data_format="file")
        tmp_inf = vic_frame.inf_frame.point_cloud(data_format="file")
        
        trans = vic_frame.transform('Infrastructure_lidar','Vehicle_lidar')
        rotation, translation = trans.get_rot_trans()
        result, _ = inference_detector_feature_fusion(self.model, tmp_veh, tmp_inf, rotation, translation, vic_frame)
        box, box_ry,  box_center,  arrow_ends = get_box_info(result)
        
        remain = []
        if len(result[0]["boxes_3d"].tensor) != 0:
            for i in range(box.shape[0]):
                if filt(box[i]):
                    remain.append(i)
        if len(remain) >= 1:
            box =box[remain]
            box_center = box_center[remain]
            arrow_ends = arrow_ends[remain]
            result[0]["scores_3d"]=result[0]["scores_3d"].numpy()[remain]
            result[0]["labels_3d"]=result[0]["labels_3d"].numpy()[remain]
        else:
            box = np.zeros((1, 8, 3))
            box_center = np.zeros((1, 1, 3))
            arrow_ends = np.zeros((1, 1, 3))
            result[0]["labels_3d"] = np.zeros((1))
            result[0]["scores_3d"] = np.zeros((1))
        # Save results
        pred = gen_pred_dict(
                    id,
                    [],
                    box,
                    np.concatenate([box_center, arrow_ends], axis=1),
                    np.array(1),
                    result[0]["scores_3d"].tolist(),
                    result[0]["labels_3d"].tolist(),
                )
        # if self.args.save_point_cloud:
        #     # points = trans(frame.point_cloud(format="array"))
        #     points = vic_frame.point_cloud(format="array")
        # else:
        #     points = np.array([])
        for ii in range(len(pred["labels_3d"])):
                pred["labels_3d"][ii]=2
        self.pipe.send("boxes_3d",pred["boxes_3d"])
        self.pipe.send("labels_3d",pred["labels_3d"])
        self.pipe.send("scores_3d",pred["scores_3d"])

        return {
            "boxes_3d": np.array(pred["boxes_3d"]),
            "labels_3d": np.array(pred["labels_3d"]),
            "scores_3d": np.array(pred["scores_3d"]),
        }
       
if __name__ == "__main__":
    sys.path.append("..")
    sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])