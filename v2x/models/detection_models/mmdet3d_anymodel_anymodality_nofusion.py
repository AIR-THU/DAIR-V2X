import os.path as osp
import logging

logger = logging.getLogger(__name__)
import numpy as np

from dataset.dataset_utils import save_pkl, load_pkl, read_jpg
from v2x_utils import mkdir
from model_utils import init_model, inference_detector, inference_mono_3d_detector
from base_model import BaseModel
from mmdet3d_anymodel_anymodality_late import LateFusionVeh, LateFusionInf


class SingleSide(BaseModel):
    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--config-path", type=str, default="")
        parser.add_argument("--model-path", type=str, default="")
        parser.add_argument("--sensor-type", type=str, default="lidar")
        parser.add_argument("--overwrite-cache", action="store_true")

    def __init__(self, args):
        super().__init__()
        self.model = None
        self.args = args
        mkdir(osp.join(args.output, "preds"))

    def pred(self, frame, pred_filter):
        id = frame.id["camera"]
        if self.args.dataset == "dair-v2x-i":
            input_path = osp.join(self.args.input, "infrastructure-side")
        elif self.args.dataset == "dair-v2x-v":
            input_path = osp.join(self.args.input, "vehicle-side")
        path = osp.join(self.args.output, "preds", id + ".pkl")
        if not osp.exists(path) or self.args.overwrite_cache:
            logger.debug("prediction not found, predicting...")
            if self.model is None:
                raise Exception

            if self.args.sensortype == "lidar":
                result, _ = inference_detector(self.model, frame.point_cloud(data_format="file"))

            elif self.args.sensortype == "camera":
                image = osp.join(input_path, frame["image_path"])
                # tmp = "../cache/tmps_i/" + frame.id + ".jpg"  # TODO
                # if not osp.exists(tmp):
                #     import mmcv

                # mmcv.tmp = mmcv.imwrite(image, tmp)
                annos = osp.join(input_path, "annos", id + ".json")

                result, _ = inference_mono_3d_detector(self.model, image, annos)

                # hard code by yuhb
                for ii in range(len(result[0]["labels_3d"])):
                    result[0]["labels_3d"][ii] = 2

            if len(result[0]["boxes_3d"].tensor) == 0:
                box = np.zeros((1, 8, 3))
                score = np.zeros(1)
                label = np.zeros(1)
            else:
                box = result[0]["boxes_3d"].corners.numpy()
                score = result[0]["scores_3d"].numpy()
                label = result[0]["labels_3d"].numpy()

            remain = []
            for i in range(box.shape[0]):
                if pred_filter(box[i]):
                    remain.append(i)
            if len(remain) >= 1:
                box = box[remain]
                score = score[remain]
                label = label[remain]
            else:
                box = np.zeros((1, 8, 3))
                score = np.zeros(1)
                label = np.zeros(1)
            pred_dict = {
                "boxes_3d": box,
                "scores_3d": score,
                "labels_3d": label,
            }
            save_pkl(pred_dict, path)
        else:
            pred_dict = load_pkl(path)
        return pred_dict

    def forward(self, frame, pred_filter):
        try:
            pred_dict = self.pred(frame, pred_filter)
        except Exception:
            logger.info("building model")
            self.model = init_model(
                self.args.config_path,
                self.args.model_path,
                device=self.args.device,
            )
            pred_dict = self.pred(frame, pred_filter)
        return pred_dict


class InfOnly(BaseModel):
    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--inf-config-path", type=str, default="")
        parser.add_argument("--inf-model-path", type=str, default="")
        parser.add_argument("--veh-config-path", type=str, default="")
        parser.add_argument("--veh-model-path", type=str, default="")
        parser.add_argument("--no-comp", action="store_true")
        parser.add_argument("--overwrite-cache", action="store_true")

    def __init__(self, args, pipe):
        super().__init__()
        self.model = LateFusionInf(args, pipe)
        self.pipe = pipe

    def forward(self, vic_frame, filt, offset, *args):
        self.model(
            vic_frame.infrastructure_frame(),
            vic_frame.transform(from_coord="Infrastructure_lidar", to_coord="Vehicle_lidar"),
            filt,
        )
        pred = np.array(self.pipe.receive("boxes"))
        return {
            "boxes_3d": pred,
            "labels_3d": np.array(self.pipe.receive("label")),
            "scores_3d": np.array(self.pipe.receive("score")),
        }


class VehOnly(BaseModel):
    @staticmethod
    def add_arguments(parser):
        parser.add_argument("--inf-config-path", type=str, default="")
        parser.add_argument("--inf-model-path", type=str, default="")
        parser.add_argument("--veh-config-path", type=str, default="")
        parser.add_argument("--veh-model-path", type=str, default="")
        parser.add_argument("--overwrite-cache", action="store_true")

    def __init__(self, args, pipe):
        super().__init__()
        self.model = LateFusionVeh(args)
        self.pipe = pipe

    def forward(self, vic_frame, filt, *args):
        pred = self.model(vic_frame.vehicle_frame(), None, filt)[0]
        return {
            "boxes_3d": np.array(pred["boxes_3d"]),
            "labels_3d": np.array(pred["labels_3d"]),
            "scores_3d": np.array(pred["scores_3d"]),
        }
