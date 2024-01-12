import math
import numpy as np


def range2box(box_range):
    # [x0, y0, z0, x1, y1, z1]
    box_range = np.array(box_range)
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
    return np.array([[box_range[index] for index in indexs]])


def dot_product(p1, p2):
    return p1[0] * p2[0] + p1[1] * p2[1] + p1[2] * p2[2]


def GetCross(x1, y1, x2, y2, x, y):
    a = (x2 - x1, y2 - y1)
    b = (x - x1, y - y1)
    return a[0] * b[1] - a[1] * b[0]


def cross_product(p1, p2):
    return [
        p1[1] * p2[2] - p1[2] * p2[1],
        p1[2] * p2[0] - p1[0] * p2[2],
        p1[0] * p2[1] - p2[0] * p1[1],
    ]


def isInSide(x1, y1, x2, y2, x3, y3, x4, y4, x, y):
    return (
        GetCross(x1, y1, x2, y2, x, y) * GetCross(x3, y3, x4, y4, x, y) >= 0
        and GetCross(x2, y2, x3, y3, x, y) * GetCross(x4, y4, x1, y1, x, y) >= 0
    )


def above_plane(point, plane):
    # ax + by + cz = d
    norm = cross_product(plane[1] - plane[0], plane[2] - plane[0])  # [a, b, c]
    d = dot_product(plane[0], norm)
    z_intersec = (d - norm[0] * point[0] - norm[1] * point[1]) / norm[2]
    # https://www.cnblogs.com/nobodyzhou/p/6145030.html
    t = (norm[0] * point[0] + norm[1] * point[1] + norm[2] * point[2] - d) / (
        norm[0] ** 2 + norm[1] ** 2 + norm[2] ** 2
    )
    point_x = point[0] - norm[0] * t
    point_y = point[1] - norm[1] * t
    if z_intersec <= point[2] and isInSide(
        plane[0][0],
        plane[0][1],
        plane[1][0],
        plane[1][1],
        plane[2][0],
        plane[2][1],
        plane[3][0],
        plane[3][1],
        point_x,
        point_y,
    ):
        # if z_intersec <= point[2] and point_in_matrix([point_x,point_y], plane[:, :2]):
        return 1
    else:
        return 0


def point_in_box(point, box):
    return above_plane(point, box[:4]) + above_plane(point, box[4:]) == 1


def get_lidar_3d_8points(label_3d_dimensions, lidar_3d_location, rotation_z):
    lidar_rotation = np.matrix(
        [
            [math.cos(rotation_z), -math.sin(rotation_z), 0],
            [math.sin(rotation_z), math.cos(rotation_z), 0],
            [0, 0, 1]
        ]
    )
    l, w, h = label_3d_dimensions
    corners_3d_lidar = np.matrix(
        [
            [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2],
            [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2],
            [-h / 2, -h / 2, -h / 2, -h / 2, h / 2, h / 2, h / 2, h / 2],
        ]
    )
    lidar_3d_8points = lidar_rotation * corners_3d_lidar + np.matrix(lidar_3d_location).T
    return lidar_3d_8points.T.tolist()


class Filter(object):
    def __init__(self):
        pass

    def __call__(self, **args):
        return True


class RectFilter(Filter):
    def __init__(self, bbox):
        super().__init__()
        self.bbox = bbox

    def __call__(self, box, **args):
        for corner in box:
            if point_in_box(corner, self.bbox):
                return True
        return False