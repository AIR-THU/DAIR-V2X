import os
import json
import numpy as np
from pypcd import pypcd


def read_pcd(path_pcd):
    return pypcd.PointCloud.from_path(path_pcd)


def concatenate_pcd2bin(pc1, pc2, path_save):
    np_x1 = (np.array(pc1.pc_data["x"], dtype=np.float32)).astype(np.float32)
    np_y1 = (np.array(pc1.pc_data["y"], dtype=np.float32)).astype(np.float32)
    np_z1 = (np.array(pc1.pc_data["z"], dtype=np.float32)).astype(np.float32)
    np_i1 = (np.array(pc1.pc_data["intensity"], dtype=np.float32)).astype(np.float32) / 255

    np_x2 = (np.array(pc2.pc_data["x"], dtype=np.float32)).astype(np.float32)
    np_y2 = (np.array(pc2.pc_data["y"], dtype=np.float32)).astype(np.float32)
    np_z2 = (np.array(pc2.pc_data["z"], dtype=np.float32)).astype(np.float32)
    np_i2 = (np.array(pc2.pc_data["intensity"], dtype=np.float32)).astype(np.float32)

    np_x = np.append(np_x1, np_x2)
    np_y = np.append(np_y1, np_y2)
    np_z = np.append(np_z1, np_z2)
    np_i = np.append(np_i1, np_i2)
    points_32 = np.transpose(np.vstack((np_x, np_y, np_z, np_i)))
    list_pcd = []
    for i in range(len(points_32)):

        x, y, z, intensity = points_32[i][0], points_32[i][1], points_32[i][2], points_32[i][3]
        list_pcd.append((x, y, z, intensity))
    dt = np.dtype([("x", "f4"), ("y", "f4"), ("z", "f4"), ("intensity", "f4")])
    np_pcd = np.array(list_pcd, dtype=dt)
    new_metadata = {}
    new_metadata["version"] = "0.7"
    new_metadata["fields"] = ["x", "y", "z", "intensity"]
    new_metadata["size"] = [4, 4, 4, 4]
    new_metadata["type"] = ["F", "F", "F", "F"]
    new_metadata["count"] = [1, 1, 1, 1]
    new_metadata["width"] = len(np_pcd)
    new_metadata["height"] = 1
    new_metadata["viewpoint"] = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    new_metadata["points"] = len(np_pcd)
    new_metadata["data"] = "binary"
    pc_save = pypcd.PointCloud(new_metadata, np_pcd)
    pc_save.save_pcd(path_save, compression="binary_compressed")
