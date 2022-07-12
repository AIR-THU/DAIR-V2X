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


def cross_product(p1, p2):
    return [
        p1[1] * p2[2] - p1[2] * p2[1],
        p1[2] * p2[0] - p1[0] * p2[2],
        p1[0] * p2[1] - p2[0] * p1[1],
    ]


def above_line(point, st, ed):
    # ax + by = c
    a = ed[1] - st[1]
    b = st[0] - ed[0]
    c = st[0] * ed[1] - ed[0] * st[1]
    if abs(b) > 1e-6 and abs(a) > 1e-6:
        y_intersec = (c - a * point[0]) / b
        return (
            y_intersec >= st[1] and y_intersec <= ed[1] or y_intersec >= ed[1] and y_intersec <= st[1]
        ) and y_intersec < point[1]
    elif abs(b) > 1e-6:
        return (point[0] >= st[0] and point[0] <= ed[0] or point[0] >= ed[0] and point[0] <= st[0]) and point[1] >= st[
            1
        ]
    else:
        return 0


def point_in_matrix(point, matrix):
    point
    return (
        above_line(point, matrix[0], matrix[1])
        + above_line(point, matrix[1], matrix[2])
        + above_line(point, matrix[2], matrix[3])
        + above_line(point, matrix[3], matrix[0])
    ) % 2 == 1


def GetCross(x1, y1, x2, y2, x, y):
    a = (x2 - x1, y2 - y1)
    b = (x - x1, y - y1)
    return a[0] * b[1] - a[1] * b[0]


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
