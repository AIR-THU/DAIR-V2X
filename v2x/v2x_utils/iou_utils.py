import numpy as np
from scipy.spatial import ConvexHull


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
