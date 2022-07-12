import numpy as np
from scipy.spatial import ConvexHull
from functools import cmp_to_key
import logging

logger = logging.getLogger(__name__)

from config import superclass

iou_threshold_dict = {
    "car": [0.3, 0.5, 0.7],
    "cyclist": [0.25, 0.5],
    "pedestrian": [0.25, 0.5],
}


def polygon_clip(subjectPolygon, clipPolygon):
    """Clip a polygon with another polygon.

     Ref: https://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping#Python

     Args:
       subjectPolygon: a list of (x,y) 2d points, any polygon.
       clipPolygon: a list of (x,y) 2d points, has to be *convex*
    Note:
      **points have to be counter-clockwise ordered**

    Return:
      a list of (x,y) vertex point for the intersection polygon.
    """

    def inside(p):
        return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) > (cp2[1] - cp1[1]) * (p[0] - cp1[0])

    def computeIntersection():
        dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
        dp = [s[0] - e[0], s[1] - e[1]]
        n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
        n2 = s[0] * e[1] - s[1] * e[0]
        n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
        return [(n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3]

    outputList = subjectPolygon
    cp1 = clipPolygon[-1]

    for clipVertex in clipPolygon:
        cp2 = clipVertex
        inputList = outputList
        outputList = []
        s = inputList[-1]

        for subjectVertex in inputList:
            e = subjectVertex
            if inside(e):
                if not inside(s):
                    outputList.append(computeIntersection())
                outputList.append(e)
            elif inside(s):
                outputList.append(computeIntersection())
            s = e
        cp1 = cp2
        if len(outputList) == 0:
            return None
    return outputList


def poly_area(x, y):
    """Ref: http://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates"""
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def convex_hull_intersection(p1, p2):
    """Compute area of two convex hull's intersection area.
    p1,p2 are a list of (x,y) tuples of hull vertices.
    return a list of (x,y) for the intersection and its volume
    """
    inter_p = polygon_clip(p1, p2)
    if inter_p is not None:
        hull_inter = ConvexHull(inter_p)
        return inter_p, hull_inter.volume
    else:
        return None, 0.0


def box3d_vol(corners, debug=False):
    """corners: (8,3) no assumption on axis direction"""
    a = np.sqrt(np.sum((corners[0, :] - corners[1, :]) ** 2))
    b = np.sqrt(np.sum((corners[1, :] - corners[2, :]) ** 2))
    c = np.sqrt(np.sum((corners[0, :] - corners[4, :]) ** 2))
    return a * b * c


def is_clockwise(p):
    x = p[:, 0]
    y = p[:, 1]
    return np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)) > 0


def box3d_iou(corners1, corners2, debug=False):
    """Compute 3D bounding box IoU.

    Input:
        corners1:         numpy array (8,3)
        corners2:         numpy array (8,3)

    Output:
        iou:    3D bounding box IoU
        iou_2d: bird's eye view 2D bounding box IoU
    """
    # corner points are in counter clockwise order
    rect1 = [(corners1[i, 0], corners1[i, 1]) for i in range(4)]
    rect2 = [(corners2[i, 0], corners2[i, 1]) for i in range(4)]

    area1 = poly_area(np.array(rect1)[:, 0], np.array(rect1)[:, 1])
    area2 = poly_area(np.array(rect2)[:, 0], np.array(rect2)[:, 1])

    inter, inter_area = convex_hull_intersection(rect1, rect2)
    iou_2d = inter_area / (area1 + area2 - inter_area)
    if debug:
        print("area=", inter_area, "iou=", iou_2d)
    zmax = min(corners1[4, 2], corners2[4, 2])
    zmin = max(corners1[0, 2], corners2[0, 2])
    if debug:
        print("zmax=", zmax, "zmin=", zmin)

    inter_vol = inter_area * max(0.0, zmax - zmin)

    vol1 = box3d_vol(corners1, debug)
    vol2 = box3d_vol(corners2, debug)
    iou = inter_vol / (vol1 + vol2 - inter_vol)
    if debug:
        print(inter_vol, vol1, vol2)
    return iou, iou_2d


"""
box corner order: (x0y0z0, x0y0z1, x0y1z1, x0y1z0, x1y0z0, x1y0z1, x1y1z1, x1y1z0)
                                 up z
                  front x         ^
                     /            |
                    /             |
      (x1, y0, z1) + ------------ + (x1, y1, z1)
                  /|            / |
                 / |           /  |
   (x0, y0, z1) + ----------- +   + (x1, y1, z0)
                |  /      .   |  /
                | / origin    | /
left y<-------- + ----------- + (x0, y1, z0)
            (x0, y0, z0)
"""
perm_pred = [0, 4, 7, 3, 1, 5, 6, 2]
perm_label = [3, 2, 1, 0, 7, 6, 5, 4]


def cmp(pred1, pred2):
    if pred1["score"] > pred2["score"]:
        return -1
    elif pred1["score"] < pred2["score"]:
        return 1
    else:
        return 0


def build_label_list(annos, filt):
    result_list = []
    for i in range(len(annos["labels_3d"])):
        if superclass[annos["labels_3d"][i]] == filt:
            result_list.append({"box": annos["boxes_3d"][i], "score": annos["scores_3d"][i]})
    return result_list


def compute_type(gt_annos, pred_annos, cla, iou_threshold, view):
    """
    Input:
        gt_annos, pred_annos: Dict, {'boxes_3d': Array[N, 8, 3], 'labels_3d': Array[N], 'scores_3d': Array[N]}
        cla:                  Str, Class of interest
        iou threshold:        Float
        view:                 Str, 3d or bev
    Output:
        result_pred_annos:    List, [{'box': Array[8, 3], 'score': Float, 'type': 'tp'/'fp'}]
        num_gt:               Int, number of ground truths
    """
    gt_annos = build_label_list(gt_annos, filt=cla)
    pred_annos = build_label_list(pred_annos, filt=cla)
    pred_annos = sorted(pred_annos, key=cmp_to_key(cmp))
    result_pred_annos = []
    num_tp = 0
    p, q = len(pred_annos), len(gt_annos)
    for i in range(len(pred_annos)):
        pred_annos[i]["id"] = i
    for gt_anno in gt_annos:
        # logger.debug("ground truth center: {}".format(np.mean(gt_anno["box"], axis=0)))
        mx = iou_threshold
        mx_pred = None
        for i in range(len(pred_annos)):
            pred_anno = pred_annos[i]
            try:
                iou, iou_2d = box3d_iou(gt_anno["box"][perm_label], pred_anno["box"][perm_pred])
            except Exception:
                iou, iou_2d = 0, 0
                # print("gt=", gt_anno['box'][perm_label], "pred=", pred_anno['box'][perm_pred])
            if view == "bev":
                iou = iou_2d
            """
            if np.sum((np.mean(gt_anno["box"], axis=0) - np.mean(pred_anno['box'], axis=0)) ** 2) ** 0.5 < 3:
                logger.info("pred center:{} {}".format(pred_anno["id"], np.mean(pred_anno['box'], axis=0)))
                logger.info("iou: {}".format(iou))
                if iou < 0.5:
                    iou, _ = box3d_iou(gt_anno['box'][perm_label], pred_anno['box'][perm_pred], debug=True)
            """
            if iou >= mx:

                mx = iou
                mx_pred = i
        if mx_pred is not None:
            result_pred_annos.append(pred_annos[mx_pred])
            del pred_annos[mx_pred]
            result_pred_annos[-1]["type"] = "tp"
            num_tp += 1
    for pred_anno in pred_annos:
        pred_anno["type"] = "fp"
        result_pred_annos.append(pred_anno)
    logger.debug("num_tp: {}, pred: {}, gt: {}".format(num_tp, p, q))
    return result_pred_annos, len(gt_annos), num_tp


def compute_ap(pred_annos, num_gt):
    """
    Input:
        pred_annos: List, [{'box': Array[8, 3], 'score': Float, 'type': 'tp'/'fp'}]
        num_gt:     Int, number of ground truths
    Output:
        mAP:        Float, evaluation result
    """
    pred_annos = sorted(pred_annos, key=cmp_to_key(cmp))
    num_tp = np.zeros(len(pred_annos))
    for i in range(len(pred_annos)):
        num_tp[i] = 0 if i == 0 else num_tp[i - 1]
        if pred_annos[i]["type"] == "tp":
            num_tp[i] += 1
    # logger.debug("num tp = {}".format(num_tp))
    precision = num_tp / np.arange(1, len(pred_annos) + 1)
    recall = num_tp / num_gt
    for i in range(len(pred_annos) - 1, 0, -1):
        precision[i - 1] = max(precision[i], precision[i - 1])
    index = np.where(recall[1:] != recall[:-1])[0]
    return np.sum((recall[index + 1] - recall[index]) * precision[index + 1])


class Evaluator(object):
    def __init__(self, pred_classes):
        self.pred_classes = pred_classes
        self.all_preds = {"3d": {}, "bev": {}}
        self.gt_num = {}
        for pred_class in self.pred_classes:
            self.all_preds["3d"][pred_class] = {}
            self.all_preds["bev"][pred_class] = {}
            self.gt_num[pred_class] = {}
            for iou in iou_threshold_dict[pred_class]:
                self.all_preds["3d"][pred_class][iou] = []
                self.all_preds["bev"][pred_class][iou] = []
                self.gt_num[pred_class][iou] = 0

    def add_frame(self, pred, label):
        for pred_class in self.pred_classes:
            for iou in iou_threshold_dict[pred_class]:
                pred_result, num_label, num_tp = compute_type(label, pred, pred_class, iou, "3d")  # test
                self.all_preds["3d"][pred_class][iou] += pred_result
                self.all_preds["bev"][pred_class][iou] += compute_type(label, pred, pred_class, iou, "bev")[0]
                self.gt_num[pred_class][iou] += num_label
                # logger.debug("iou: {}, tp: {}, all_pred: {}".format(iou, num_tp, len(pred["labels_3d"])))

    def print_ap(self, view, type="micro"):
        for pred_class in self.pred_classes:
            for iou in iou_threshold_dict[pred_class]:
                ap = compute_ap(self.all_preds[view][pred_class][iou], self.gt_num[pred_class][iou])
                print("%s %s IoU threshold %.2lf, Average Precision = %.2lf" % (pred_class, view, iou, ap * 100))
