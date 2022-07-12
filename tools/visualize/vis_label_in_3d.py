import os.path as osp
import numpy as np
import mayavi.mlab as mlab
import pickle
import argparse
import math
from pypcd import pypcd
import json
from vis_utils import id_to_str, load_pkl


def draw_boxes3d(
    boxes3d, fig, arrows=None, color=(1, 0, 0), line_width=2, draw_text=True, text_scale=(1, 1, 1), color_list=None
):
    """
    boxes3d: numpy array (n,8,3) for XYZs of the box corners
    fig: mayavi figure handler
    color: RGB value tuple in range (0,1), box line color
    line_width: box line width
    draw_text: boolean, if true, write box indices beside boxes
    text_scale: three number tuple
    color_list: RGB tuple
    """
    num = len(boxes3d)
    for n in range(num):
        if arrows is not None:
            mlab.plot3d(
                arrows[n, :, 0],
                arrows[n, :, 1],
                arrows[n, :, 2],
                color=color,
                tube_radius=None,
                line_width=line_width,
                figure=fig,
            )
        b = boxes3d[n]
        if color_list is not None:
            color = color_list[n]
        if draw_text:
            mlab.text3d(b[4, 0], b[4, 1], b[4, 2], "%d" % n, scale=text_scale, color=color, figure=fig)
        for k in range(0, 4):
            i, j = k, (k + 1) % 4
            mlab.plot3d(
                [b[i, 0], b[j, 0]],
                [b[i, 1], b[j, 1]],
                [b[i, 2], b[j, 2]],
                color=color,
                tube_radius=None,
                line_width=line_width,
                figure=fig,
            )

            i, j = k + 4, (k + 1) % 4 + 4
            mlab.plot3d(
                [b[i, 0], b[j, 0]],
                [b[i, 1], b[j, 1]],
                [b[i, 2], b[j, 2]],
                color=color,
                tube_radius=None,
                line_width=line_width,
                figure=fig,
            )

            i, j = k, k + 4
            mlab.plot3d(
                [b[i, 0], b[j, 0]],
                [b[i, 1], b[j, 1]],
                [b[i, 2], b[j, 2]],
                color=color,
                tube_radius=None,
                line_width=line_width,
                figure=fig,
            )
    return fig


def read_bin(path):
    pointcloud = np.fromfile(path, dtype=np.float32, count=-1).reshape([-1, 4])
    print(pointcloud.shape)
    x = pointcloud[:, 0]
    y = pointcloud[:, 1]
    z = pointcloud[:, 2]
    return x, y, z


def read_pcd(pcd_path):
    pcd = pypcd.PointCloud.from_path(pcd_path)

    x = np.transpose(pcd.pc_data["x"])
    y = np.transpose(pcd.pc_data["y"])
    z = np.transpose(pcd.pc_data["z"])
    return x, y, z


def get_lidar_3d_8points(obj_size, yaw_lidar, center_lidar):
    center_lidar = [center_lidar[0], center_lidar[1], center_lidar[2]]

    lidar_r = np.matrix(
        [[math.cos(yaw_lidar), -math.sin(yaw_lidar), 0], [math.sin(yaw_lidar), math.cos(yaw_lidar), 0], [0, 0, 1]]
    )
    l, w, h = obj_size
    center_lidar[2] = center_lidar[2] - h / 2
    corners_3d_lidar = np.matrix(
        [
            [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2],
            [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2],
            [0, 0, 0, 0, h, h, h, h],
        ]
    )
    corners_3d_lidar = lidar_r * corners_3d_lidar + np.matrix(center_lidar).T

    return corners_3d_lidar.T


def read_label_bboxes(label_path):
    with open(label_path, "r") as load_f:
        labels = json.load(load_f)

    boxes = []
    for label in labels:
        obj_size = [
            float(label["3d_dimensions"]["l"]),
            float(label["3d_dimensions"]["w"]),
            float(label["3d_dimensions"]["h"]),
        ]
        yaw_lidar = float(label["rotation"])
        center_lidar = [
            float(label["3d_location"]["x"]),
            float(label["3d_location"]["y"]),
            float(label["3d_location"]["z"]),
        ]

        box = get_lidar_3d_8points(obj_size, yaw_lidar, center_lidar)
        boxes.append(box)

    return boxes


def plot_box_pcd(x, y, z, boxes):
    vals = "height"
    if vals == "height":
        col = z
    fig = mlab.figure(bgcolor=(0, 0, 0), size=(640, 500))
    mlab.points3d(
        x,
        y,
        z,
        col,  # Values used for Color
        mode="point",
        colormap="spectral",  # 'bone', 'copper', 'gnuplot'
        color=(1, 1, 0),  # Used a fixed (r,g,b) instead
        figure=fig,
    )
    draw_boxes3d(np.array(boxes), fig, arrows=None)

    mlab.axes(xlabel="x", ylabel="y", zlabel="z")
    mlab.show()


def plot_pred_fusion(args):
    fig = mlab.figure(bgcolor=(1, 1, 1), size=(640, 500))
    data_all = load_pkl(osp.join(args.path, "result", id_to_str(args.id) + ".pkl"))
    print(data_all.keys())

    draw_boxes3d(
        np.array(data_all["boxes_3d"]),
        fig,
        color=(32 / 255, 32 / 255, 32 / 255),
        line_width=1,
    )
    draw_boxes3d(
        np.array(data_all["label"]),
        fig,
        color=(0, 0, 255 / 255),
    )
    mlab.show()


def plot_pred_single(args):
    fig = mlab.figure(bgcolor=(1, 1, 1), size=(1280, 1000))
    path = args.path
    file = id_to_str(args.id) + ".pkl"

    data_label = load_pkl(osp.join(path, "result", file))
    label_3d_bboxes = data_label["boxes_3d"]
    if len(label_3d_bboxes.shape) != 3:
        label_3d_bboxes = label_3d_bboxes.squeeze(axis=0)

    data_pred = load_pkl(osp.join(path, "preds", file))
    pred_3d_bboxes = data_pred["boxes_3d"]

    draw_boxes3d(label_3d_bboxes, fig, color=(0, 1, 0))  # vis_label
    draw_boxes3d(pred_3d_bboxes, fig, color=(1, 0, 0))  # vis_pred

    mlab.show()


def plot_label_pcd(args):
    pcd_path = args.pcd_path
    x, y, z = read_pcd(pcd_path)

    label_path = args.label_path
    boxes = read_label_bboxes(label_path)

    plot_box_pcd(x, y, z, boxes)


def add_arguments(parser):
    parser.add_argument("--task", type=str, default="coop", choices=["fusion", "single", "pcd_label"])
    parser.add_argument("--path", type=str, default="./coop-mono_v50100")
    parser.add_argument("--id", type=int, default=0)
    parser.add_argument("--pcd-path", type=str, default="./000029.bin", help="pcd path to visualize")
    parser.add_argument("--label-path", type=str, default="./000029.json", help="label path to visualize")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.task == "fusion":
        plot_pred_fusion(args)

    if args.task == "single":
        plot_pred_single(args)

    if args.task == "pcd_label":
        plot_label_pcd(args)
