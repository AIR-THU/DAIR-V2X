import os.path as osp
from functools import cmp_to_key
import logging

logger = logging.getLogger(__name__)

from base_dataset import DAIRV2XDataset, get_annos, build_path_to_info
from dataset.dataset_utils import load_json, InfFrame, VehFrame, VICFrame, Label
from v2x_utils import Filter, RectFilter, id_cmp, id_to_str, get_trans, box_translation


class DAIRV2XI(DAIRV2XDataset):
    def __init__(self, path, args, split="train", sensortype="lidar", extended_range=None):
        super().__init__(path, args, split, extended_range)
        data_infos = load_json(osp.join(path, "infrastructure-side/data_info.json"))
        split_path = args.split_data_path
        data_infos = self.get_split(split_path, split, data_infos)

        self.inf_path2info = build_path_to_info(
            "",
            load_json(osp.join(path, "infrastructure-side/data_info.json")),
            sensortype,
        )

        self.data = []
        for elem in data_infos:
            gt_label = {}
            filt = RectFilter(extended_range[0]) if extended_range is not None else Filter()
            gt_label["camera"] = Label(osp.join(path, "infrastructure-side", elem["label_camera_std_path"]), filt)
            gt_label["lidar"] = Label(osp.join(path, "infrastructure-side", elem["label_lidar_std_path"]), filt)

            self.data.append((InfFrame(path, elem), gt_label, filt))

            if sensortype == "camera":
                inf_frame = self.inf_path2info[elem["image_path"]]
                get_annos(path + "/infrastructure-side", "", inf_frame, "camera")

    def get_split(self, split_path, split, data_infos):
        if osp.exists(split_path):
            split_data = load_json(split_path)
        else:
            print("Split File Doesn't Exists!")
            raise Exception

        if split in ["train", "val", "test"]:
            split_data = split_data[split]
        else:
            print("Split Method Doesn't Exists!")
            raise Exception

        frame_pairs_split = []
        for data_info in data_infos:
            frame_idx = data_info["image_path"].split("/")[-1].replace(".jpg", "")
            if frame_idx in split_data:
                frame_pairs_split.append(data_info)

        return frame_pairs_split

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)


class DAIRV2XV(DAIRV2XDataset):
    def __init__(self, path, args, split="train", sensortype="lidar", extended_range=None):
        super().__init__(path, args, split, extended_range)
        data_infos = load_json(osp.join(path, "vehicle-side/data_info.json"))
        split_path = args.split_data_path
        data_infos = self.get_split(split_path, split, data_infos)

        self.veh_path2info = build_path_to_info(
            "",
            load_json(osp.join(path, "vehicle-side/data_info.json")),
            sensortype,
        )

        self.data = []
        for elem in data_infos:
            gt_label = {}
            filt = RectFilter(extended_range[0]) if extended_range is not None else Filter
            for view in ["camera", "lidar"]:
                gt_label[view] = Label(osp.join(path, "vehicle-side", elem["label_" + view + "_std_path"]), filt)

            self.data.append((VehFrame(path, elem), gt_label, filt))

            if sensortype == "camera":
                veh_frame = self.veh_path2info[elem["image_path"]]
                get_annos(path + "/vehicle-side", "", veh_frame, "camera")

    def get_split(self, split_path, split, data_infos):
        if osp.exists(split_path):
            split_data = load_json(split_path)
        else:
            print("Split File Doesn't Exists!")
            raise Exception

        if split in ["train", "val", "test"]:
            split_data = split_data[split]
        else:
            print("Split Method Doesn't Exists!")
            raise Exception

        frame_pairs_split = []
        for data_info in data_infos:
            frame_idx = data_info["image_path"].split("/")[-1].replace(".jpg", "")
            if frame_idx in split_data:
                frame_pairs_split.append(data_info)

        return frame_pairs_split

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)


class VICDataset(DAIRV2XDataset):
    def __init__(self, path, args, split="train", sensortype="lidar", extended_range=None, val_data_path=""):
        super().__init__(path + "/cooperative", args, split, extended_range)
        self.path = path
        self.inf_path2info = build_path_to_info(
            "infrastructure-side",
            load_json(osp.join(path, "infrastructure-side/data_info.json")),
            sensortype,
        )
        self.veh_path2info = build_path_to_info(
            "vehicle-side",
            load_json(osp.join(path, "vehicle-side/data_info.json")),
            sensortype,
        )

        ### Patch for FFNet evaluation ###
        if args.model =='feature_flow':
            frame_pairs = load_json(val_data_path)
        else:
            frame_pairs = load_json(osp.join(path, "cooperative/data_info.json"))
            split_path = args.split_data_path
            frame_pairs = self.get_split(split_path, split, frame_pairs)

        self.data = []
        self.inf_frames = {}
        self.veh_frames = {}

        for elem in frame_pairs:
            if sensortype == "lidar":
                inf_frame = self.inf_path2info[elem["infrastructure_pointcloud_path"]]
                veh_frame = self.veh_path2info[elem["vehicle_pointcloud_path"]]
            elif sensortype == "camera":
                inf_frame = self.inf_path2info[elem["infrastructure_image_path"]]
                veh_frame = self.veh_path2info[elem["vehicle_image_path"]]
                get_annos(path, "infrastructure-side", inf_frame, "camera")
                get_annos(path, "vehicle-side", veh_frame, "camera")

            inf_frame = InfFrame(path + "/infrastructure-side/", inf_frame)
            veh_frame = VehFrame(path + "/vehicle-side/", veh_frame)
            if not inf_frame["batch_id"] in self.inf_frames:
                self.inf_frames[inf_frame["batch_id"]] = [inf_frame]
            else:
                self.inf_frames[inf_frame["batch_id"]].append(inf_frame)
            if not veh_frame["batch_id"] in self.veh_frames:
                self.veh_frames[veh_frame["batch_id"]] = [veh_frame]
            else:
                self.veh_frames[veh_frame["batch_id"]].append(veh_frame)
            vic_frame = VICFrame(path, elem, veh_frame, inf_frame, 0)

            # filter in world coordinate
            if extended_range is not None:
                trans = vic_frame.transform(from_coord="Vehicle_lidar", to_coord="World")
                filt_world = RectFilter(trans(extended_range)[0])

            trans_1 = vic_frame.transform("World", "Vehicle_lidar")
            label_v = Label(osp.join(path, elem["cooperative_label_path"]), filt_world)
            label_v["boxes_3d"] = trans_1(label_v["boxes_3d"])
            filt = RectFilter(extended_range[0])
            tup = (
                vic_frame,
                label_v,
                filt,
            )
            self.data.append(tup)

    def query_veh_segment(self, frame, sensortype="lidar", previous_only=False):
        segment = self.veh_frames[frame.batch_id]
        return [f for f in segment if f.id[sensortype] < frame.id[sensortype] or not previous_only]

    def query_inf_segment(self, frame, sensortype="lidar", previous_only=False):
        segment = self.inf_frames[frame.batch_id]
        return [f for f in segment if f.id[sensortype] < frame.id[sensortype] or not previous_only]

    def get_split(self, split_path, split, frame_pairs):
        if osp.exists(split_path):
            split_data = load_json(split_path)
        else:
            print("Split File Doesn't Exists!")
            raise Exception

        if split in ["train", "val", "test"]:
            split_data = split_data["cooperative_split"][split]
        else:
            print("Split Method Doesn't Exists!")
            raise Exception

        frame_pairs_split = []
        for frame_pair in frame_pairs:
            veh_frame_idx = frame_pair["vehicle_image_path"].split("/")[-1].replace(".jpg", "")
            if veh_frame_idx in split_data:
                frame_pairs_split.append(frame_pair)
        return frame_pairs_split

    def __getitem__(self, index):
        raise NotImplementedError


class VICSyncDataset(VICDataset):
    def __init__(self, path, args, split="train", sensortype="lidar", extended_range=None, val_data_path=""):
        super().__init__(path, args, split, sensortype, extended_range, val_data_path)
        logger.info("VIC-Sync {} dataset, overall {} frames".format(split, len(self.data)))

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)


class VICAsyncDataset(VICDataset):
    def __init__(self, path, args, split="train", sensortype="lidar", extended_range=None, val_data_path=""):
        super().__init__(path, args, split, sensortype, extended_range)
        self.k = args.k
        self.async_data = []
        for vic_frame, coop_labels, filt in self.data:
            inf_frame, delta_t = self.prev_inf_frame(
                vic_frame.inf_frame.id[sensortype],
                sensortype,
            )
            if inf_frame is None:
                continue
            else:
                new_vic_frame = VICFrame(path, {}, vic_frame.veh_frame, inf_frame, delta_t, vic_frame.offset)
                self.async_data.append((new_vic_frame, coop_labels, filt))

        logger.info("VIC-Async {} dataset, overall {} frames".format(split, len(self.async_data)))

    def __getitem__(self, index):
        return self.async_data[index]

    def __len__(self):
        return len(self.async_data)

    def prev_inf_frame(self, index, sensortype="lidar"):
        if sensortype == "lidar":
            cur = self.inf_path2info["infrastructure-side/velodyne/" + index + ".pcd"]
            if (
                int(index) - self.k < int(cur["batch_start_id"])
                or "infrastructure-side/velodyne/" + id_to_str(int(index) - self.k) + ".pcd" not in self.inf_path2info
            ):
                return None, None
            prev = self.inf_path2info["infrastructure-side/velodyne/" + id_to_str(int(index) - self.k) + ".pcd"]
            return (
                InfFrame(self.path + "/infrastructure-side/", prev),
                (int(cur["pointcloud_timestamp"]) - int(prev["pointcloud_timestamp"])) / 1000.0,
            )
        elif sensortype == "camera":
            cur = self.inf_path2info["infrastructure-side/image/" + index + ".jpg"]
            if int(index) - self.k < int(cur["batch_start_id"]):
                return None, None
            prev = self.inf_path2info["infrastructure-side/image/" + id_to_str(int(index) - self.k) + ".jpg"]
            get_annos(self.path, "infrastructure-side", prev, "camera")
            return (
                InfFrame(self.path + "/infrastructure-side/", prev),
                (int(cur["image_timestamp"]) - int(prev["image_timestamp"])) / 1000.0,
            )


if __name__ == "__main__":
    from tqdm import tqdm
    import numpy as np

    input = "../data/cooperative-vehicle-infrastructure/"
    split = "val"
    sensortype = "camera"
    box_range = np.array([-10, -49.68, -3, 79.12, 49.68, 1])
    indexs = [
        [0, 1, 2],
        [3, 1, 2],
        [3, 4, 2],
        [0, 4, 2],
        [0, 1, 5],
        [3, 1, 5],
        [3, 4, 5],
        [0, 4, 5],
    ]
    extended_range = np.array([[box_range[index] for index in indexs]])
    dataset = VICSyncDataset(input, split, sensortype, extended_range=extended_range)

    for VICFrame_data, label, filt in tqdm(dataset):
        veh_image_path = VICFrame_data.vehicle_frame()["image_path"][-10:-4]
        inf_image_path = VICFrame_data.infrastructure_frame()["image_path"][-10:-4]
        print(veh_image_path, inf_image_path)
