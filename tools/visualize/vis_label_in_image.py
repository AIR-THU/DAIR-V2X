import os
import os.path as osp
import argparse
from vis_utils import get_cam_8_points, read_json, vis_label_in_img


def vis_label_in_image(path, save_path):
    """
    path: The root directory of the visualization image, infrastructure-side/vehicle-side.
    save_path: Output path of the visualized image.
    """
    # get data_info
    path_data_infos = read_json(osp.join(path, "data_info.json"))
    for data_info in path_data_infos:
        # Get the path of the image to be visualized.
        image_path = osp.join(path, data_info["image_path"])
        if osp.basename(path) in ["infrastructure-side", "single-infrastructure-side"]:
            # visualize infrastructure-side image
            label_path = osp.join(path, data_info["label_camera_std_path"])
            lidar2cam_path = osp.join(
                path, data_info["calib_virtuallidar_to_camera_path"]
            )  # extrinsic of lidar_to_camera
        else:
            # visualize vehicle-side image
            label_path = osp.join(path, data_info["label_lidar_std_path"])
            lidar2cam_path = osp.join(path, data_info["calib_lidar_to_camera_path"])  # extrinsic of lidar_to_camera

        labels = []
        oris = read_json(label_path)
        for ori in oris:
            if "rotation" not in ori.keys():
                ori["rotation"] = 0.0
            labels.append([ori["3d_dimensions"], ori["3d_location"], ori["rotation"]])

        cam_instrinsic_path = osp.join(path, data_info["calib_camera_intrinsic_path"])  # intrinsic pf camera

        camera_8_points_list = get_cam_8_points(
            labels, lidar2cam_path
        )  # Convert the label to the 8 points of the cameara coordinate system
        vis_label_in_img(camera_8_points_list, image_path, cam_instrinsic_path, save_path)


def add_arguments(parser):
    parser.add_argument(
        "--path",
        type=str,
        default="./cooperative-vehicle-infrastructure/vehicle-side",
    )
    parser.add_argument("--id", type=int, default=0)
    parser.add_argument("--output-file", type=str, default="./veh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if not osp.exists(args.output_file):
        os.mkdir(args.output_file)

    vis_label_in_image(args.path, args.output_file)
