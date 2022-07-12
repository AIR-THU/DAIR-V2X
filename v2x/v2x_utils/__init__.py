import os
import os.path as osp

from .transformation_utils import *
from .geometry_utils import *
from .filter_utils import *
from .eval_utils import *
from .iou_utils import *


def id_to_str(id, digits=6):
    result = ""
    for i in range(digits):
        result = str(id % 10) + result
        id //= 10
    return result


def mkdir(path):
    if not osp.exists(path):
        os.system("mkdir " + path)


def id_cmp(x, y):
    id_x = int(x["pointcloud_path"][-10:-4])
    id_y = int(y["pointcloud_path"][-10:-4])
    if id_x < id_y:
        return -1
    elif id_x == id_y:
        return 0
    else:
        return 1
