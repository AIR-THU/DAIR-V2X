import numpy as np

from v2x_utils import get_3d_8points
from dataset.dataset_utils import load_json
from config import name2id


class Label(dict):
    def __init__(self, path, filt):
        raw_labels = load_json(path)
        boxes = []
        class_types = []
        for label in raw_labels:
            size = label["3d_dimensions"]
            if size["l"] == 0 or size["w"] == 0 or size["h"] == 0:
                continue
            if "world_8_points" in label:
                box = label["world_8_points"]
            else:
                pos = label["3d_location"]
                box = get_3d_8points(
                    [float(size["l"]), float(size["w"]), float(size["h"])],
                    float(label["rotation"]),
                    [float(pos["x"]), float(pos["y"]), float(pos["z"]) - float(size["h"]) / 2],
                ).tolist()
            # determine if box is in extended range
            if filt is None or filt(box):
                boxes.append(box)
                class_types.append(name2id[label["type"].lower()])
        boxes = np.array(boxes)
        class_types = np.array(class_types)
        # if len(class_types) == 1:
        #     boxes = boxes[np.newaxis, :]
        self.__setitem__("boxes_3d", boxes)
        self.__setitem__("labels_3d", class_types)
        self.__setitem__("scores_3d", np.ones_like(class_types))
