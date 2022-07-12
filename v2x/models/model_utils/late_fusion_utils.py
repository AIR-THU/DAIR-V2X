import numpy as np
import pickle
from scipy.optimize import linear_sum_assignment
from sklearn.linear_model import LinearRegression

inf = 1e42  # infinity


def box2info(boxes):
    num_boxes = boxes.shape[0]
    center = np.mean(boxes, axis=1)
    size = np.zeros((num_boxes, 3))
    size[:, 0] = (
        np.sum((boxes[:, 2, :] - boxes[:, 1, :]) ** 2, axis=1) ** 0.5
        + np.sum((boxes[:, 6, :] - boxes[:, 5, :]) ** 2, axis=1) ** 0.5
    ) / 2
    size[:, 1] = (
        np.sum((boxes[:, 4, :] - boxes[:, 0, :]) ** 2, axis=1) ** 0.5
        + np.sum((boxes[:, 6, :] - boxes[:, 2, :]) ** 2, axis=1) ** 0.5
    ) / 2
    size[:, 2] = (
        boxes[:, 1, :]
        + boxes[:, 2, :]
        + boxes[:, 5, :]
        + boxes[:, 6, :]
        - boxes[:, 0, :]
        - boxes[:, 3, :]
        - boxes[:, 4, :]
        - boxes[:, 7, :]
    )[:, 2] / 4
    return center, size


class BBoxList(object):
    def __init__(self, boxes, dir, label, score, class_score=None):
        """
        Data format:
        pos0, pos1, dir: numpy array [num_boxes, dim], positions and directions of the bounding box, dim = 2/3
        score: numpy array [num_boxes], confidence of each box
        class_score: numpy array [num_boxes, num_classes], predicted probability of each class
        t: float, timestamp
        """
        self.num_boxes = boxes.shape[0]
        self.num_dims = boxes.shape[2]
        self.num_classes = class_score.shape[1] if class_score is not None else None
        self.boxes = boxes
        self.dir = dir
        self.label = label
        self.confidence = score
        self.class_score = class_score
        self.center, self.size = box2info(self.boxes)

    def __get_item__(self, key):
        # to be implemented
        pass

    def move_center(self, offset):
        delta = np.array(offset)  # N * 2
        if self.num_dims == 3:
            delta = np.insert(delta, 2, values=np.zeros(self.num_boxes), axis=1)  # N * 3
        delta = delta[:, np.newaxis, :]  # N * 1 * 3
        delta = np.repeat(delta, 8, axis=1)  # N * 8 * 3
        self.boxes += delta

    # TODO: implement the following apis
    def merge(self, box1):
        pass

    def filter(self, filter):
        pass

    def match(self, box1):
        pass


class StaticBBoxList(BBoxList):
    def __init__(self, filename, data_format="8points_pkl"):
        if data_format == "8points_pkl":
            """
            data = {
                'info': id,
                'timestamp': 时间戳
                'boxes_3d': 预测的3D box的八个顶点, [N, 8, 3]
                'arrows': box朝向，每个box两个点(起始点和结束点)，[N, 2, 3]
                'scores_3d': 各个box置信度, [N,]
                'labels_3d': 各个box的标签种类, [N,]
                'points': 全范围点云（输入模型的点云范围较小，所以只预测了一部分范围的box）
            }
            """

            def load_pkl(path):
                with open(path, "rb") as f:
                    return pickle.load(f)

            data = load_pkl(filename)
            boxes = np.array(data["boxes_3d"])
            self.boxes = boxes
            self.num_boxes = boxes.shape[0]
            self.num_dims = 3
            self.center = np.sum(boxes, axis=1) / 8
            self.size = np.zeros((self.num_boxes, 3))
            self.size[:, 0] = (
                np.sum((boxes[:, 2, :] - boxes[:, 1, :]) ** 2, axis=1) ** 0.5
                + np.sum((boxes[:, 6, :] - boxes[:, 5, :]) ** 2, axis=1) ** 0.5
            ) / 2
            self.size[:, 1] = (
                np.sum((boxes[:, 4, :] - boxes[:, 0, :]) ** 2, axis=1) ** 0.5
                + np.sum((boxes[:, 6, :] - boxes[:, 2, :]) ** 2, axis=1) ** 0.5
            ) / 2
            self.size[:, 2] = (
                boxes[:, 1, :]
                + boxes[:, 2, :]
                + boxes[:, 5, :]
                + boxes[:, 6, :]
                - boxes[:, 0, :]
                - boxes[:, 3, :]
                - boxes[:, 4, :]
                - boxes[:, 7, :]
            )[:, 2] / 4

            """
            arrows = np.array(data['arrows'])
            self.arrows = arrows
            self.dir = arrows[:, 1, :] - arrows[:, 0, :]
            self.features = np.concatenate((self.center, self.size), axis=1)
            """
            self.class_score = None
            self.confidence = np.array(data["scores_3d"])
            self.num_classes = 26

            self.label = np.array(data["labels_3d"])


class Matcher(object):
    def __init__(self):
        pass

    def match(self, frame1, frame2):
        raise NotImplementedError


class EuclidianMatcher(Matcher):
    def __init__(self, filter_func=None, delta_x=0.0, delta_y=0.0, delta_z=0.0):
        super(EuclidianMatcher, self).__init__()
        self.filter_func = filter_func
        self.delta = [delta_x, delta_y, delta_z]

    def match(self, frame1, frame2):
        cost_matrix = np.zeros((frame1.num_boxes, frame2.num_boxes))
        for i in range(frame1.num_boxes):
            for j in range(frame2.num_boxes):
                cost_matrix[i][j] = np.sum((frame1.center[i] + self.delta - frame2.center[j]) ** 2) ** 0.5
                if self.filter_func is not None and not self.filter_func(frame1, frame2, i, j):
                    cost_matrix[i][j] = 1e6
        # print(cost_matrix, linear_sum_assignment(cost_matrix))
        index1, index2 = linear_sum_assignment(cost_matrix)
        accepted = []
        cost = 0
        for i in range(len(index1)):
            if cost_matrix[index1[i]][index2[i]] < 1e5:
                accepted.append(i)
                cost += cost_matrix[index1[i]][index2[i]]
        return (
            index1[accepted],
            index2[accepted],
            0 if len(accepted) == 0 else cost / len(accepted),
        )


class Compensator(object):
    def __init__(self, *args):
        pass

    def compensate(self, frame1, frame2, *args):
        raise NotImplementedError


class SpaceCompensator(Compensator):
    def __init__(self, minx=-1.0, maxx=1.0, miny=-1.0, maxy=1.0, iters=2, steps=5):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        self.iters = iters
        self.steps = steps

    def compensate(self, frame1, frame2):
        minx = self.minx
        maxx = self.maxx
        miny = self.miny
        maxy = self.maxy
        for iter in range(self.iters):
            best_x = 0
            best_y = 0
            mn = 1e6
            mx = 0
            for x in range(self.steps):
                for y in range(self.steps):
                    delta_x = minx + (maxx - minx) / self.steps * x
                    delta_y = miny + (maxy - miny) / self.steps * y
                    cost = np.zeros((frame1.num_boxes, frame2.num_boxes))
                    for i in range(frame1.num_boxes):
                        for j in range(frame2.num_boxes):
                            size = frame1.size[i]
                            diff = np.abs(frame1.center[i] + np.array([delta_x, delta_y, 0]) - frame2.center[j]) / size
                            cost[i][j] = np.sum(diff ** 2) ** 0.5
                            if diff[0] > 2 or diff[1] > 2 or diff[2] > 2:
                                cost[i][j] = 1e6
                    index1, index2 = linear_sum_assignment(cost)
                    val = 0
                    cnt = 0
                    for i in range(len(index1)):
                        if cost[index1[i]][index2[i]] < 1e5:
                            val += cost[index1[i]][index2[i]]
                            cnt += 1
                    if cnt > mx or cnt == mx and val < mn:
                        mx = cnt
                        mn = val
                        best_x = delta_x
                        best_y = delta_y
            # print(iter, mx, mn, best_x, best_y)
            if mx == 0:
                minx = 0
                maxx = 0
                miny = 0
                maxy = 0
                break
            range_x = (maxx - minx) / self.steps / 2
            range_y = (maxy - miny) / self.steps / 2
            minx = best_x - range_x
            maxx = best_x + range_x
            miny = best_y - range_y
            maxy = best_y + range_y

        delta_x, delta_y = (minx + maxx) / 2, (miny + maxy) / 2
        offset = np.ones((frame1.num_boxes, 2))
        offset[:, 0] *= delta_x
        offset[:, 1] *= delta_y
        return offset


class TimeCompensator(Compensator):
    def __init__(self, matcher):
        self.matcher = matcher

    def compensate(self, frame1, frame2, delta1, delta2):
        ind_prev, ind_cur, _ = self.matcher.match(frame1, frame2)
        if len(ind_prev) < 1:
            avg_offset = np.mean(frame2.center, axis=0) - np.mean(frame1.center, axis=0)
            avg_offset *= delta2 / delta1
            offset = np.ones((frame2.num_boxes, 2))
            offset[:, 0] *= avg_offset[0]
            offset[:, 1] *= avg_offset[1]
        else:
            x = frame1.center[ind_prev][:, :2]
            y = frame2.center[ind_cur][:, :2] - frame1.center[ind_prev][:, :2]
            model = LinearRegression()
            model.fit(x, y)
            offset = model.predict(frame2.center[:, :2]) * delta2 / delta1
            offset[ind_cur] = y * delta2 / delta1
        return offset


class BasicFuser(object):
    def __init__(self, perspective, trust_type, retain_type):
        # perspective:
        # infrastructure / vehicle
        # trust type:
        # lc (Linear Combination) / max
        # retain type:
        # all / main / none
        self.perspective = perspective
        self.trust_type = trust_type
        self.retain_type = retain_type

    def fuse(self, frame_r, frame_v, ind_r, ind_v):
        if self.perspective == "infrastructure":
            frame1 = frame_r
            frame2 = frame_v
            ind1 = ind_r
            ind2 = ind_v
        elif self.perspective == "vehicle":
            frame1 = frame_v
            frame2 = frame_r
            ind1 = ind_v
            ind2 = ind_r

        confidence1 = np.array(frame1.confidence[ind1])
        confidence2 = np.array(frame2.confidence[ind2])
        if self.trust_type == "max":
            confidence1 = confidence1 > confidence2
            confidence2 = 1 - confidence1
        elif self.trust_type == "main":
            confidence1 = np.ones_like(confidence1)
            confidence2 = 1 - confidence1

        center = frame1.center[ind1] * np.repeat(confidence1[:, np.newaxis], 3, axis=1) + frame2.center[
            ind2
        ] * np.repeat(confidence2[:, np.newaxis], 3, axis=1)
        boxes = (
            frame1.boxes[ind1]
            + np.repeat(center[:, np.newaxis, :], 8, axis=1)
            - np.repeat(frame1.center[ind1][:, np.newaxis, :], 8, axis=1)
        )
        label = frame1.label[ind1]
        confidence = frame1.confidence[ind1] * confidence1 + frame2.confidence[ind2] * confidence2
        # arrows = frame1.arrows[ind1]

        boxes_u = []
        label_u = []
        confidence_u = []
        # arrows_u = []
        if self.retain_type in ["all", "main"]:
            for i in range(frame1.num_boxes):
                if i not in ind1 and frame1.label[i] != -1:
                    boxes_u.append(frame1.boxes[i])
                    label_u.append(frame1.label[i])
                    confidence_u.append(frame1.confidence[i])
                    # arrows_u.append(frame1.arrows[i])

        if self.retain_type in ["all"]:
            for i in range(frame2.num_boxes):
                if i not in ind2 and frame2.label[i] != -1:
                    boxes_u.append(frame2.boxes[i])
                    label_u.append(frame2.label[i])
                    confidence_u.append(frame2.confidence[i] * 0.4)
                    # arrows_u.append(frame2.arrows[i])
        if len(boxes_u) == 0:
            result_dict = {
                "boxes_3d": boxes,
                # "arrows": arrows,
                "labels_3d": label,
                "scores_3d": confidence,
            }
        else:
            result_dict = {
                "boxes_3d": np.concatenate((boxes, np.array(boxes_u)), axis=0),
                # "arrows": np.concatenate((arrows, np.array(arrows_u)), axis=0),
                "labels_3d": np.concatenate((label, np.array(label_u)), axis=0),
                "scores_3d": np.concatenate((confidence, np.array(confidence_u)), axis=0),
            }
        return result_dict
