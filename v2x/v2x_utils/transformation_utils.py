# Copyright (c) DAIR-V2X(AIR). All rights reserved.
import numpy as np
import math
import os
import json


def get_trans(info):
    return info["translation"], info["rotation"]


def quaternion_trans(input_point, translation, rotation):
    T_matrix = np.array(translation).reshape(3, 1)
    R_matrix = np.array(rotation).reshape(3, 3)

    input = np.concatenate((np.array(input_point), np.array([1]))).reshape(4, 1)
    matrix = np.concatenate((R_matrix, T_matrix), axis=1)
    output_point = np.dot(matrix, input)
    return output_point.reshape(-1)


def box_translation(boxes, translation, rotation):
    n, c, _ = boxes.shape
    result = np.zeros(boxes.shape)
    for i in range(n):
        for j in range(c):
            result[i, j, :] = quaternion_trans(boxes[i, j, :], translation, rotation)
    return result


def points_translation(points, translation, rotation):
    result = points.copy()
    for i in range(len(points)):
        result[i, :3] = quaternion_trans(points[i, :3], translation, rotation)
    return result


def get_arrow_end(centers, angles, vector=[5, 5]):
    end = []
    for angle in angles:
        end.append([vector[0] * math.sin(angle), vector[1] * math.cos(angle), 0])
    end = np.array(end) + centers
    return end


def get_3d_8points(obj_size, yaw_lidar, center_lidar):
    # yaw_lidar = -yaw_lidar
    liadr_r = np.matrix(
        [
            [math.cos(yaw_lidar), -math.sin(yaw_lidar), 0],
            [math.sin(yaw_lidar), math.cos(yaw_lidar), 0],
            [0, 0, 1],
        ]
    )
    l, w, h = obj_size
    corners_3d_lidar = np.matrix(
        [
            [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2],
            [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2],
            [0, 0, 0, 0, h, h, h, h],
        ]
    )
    corners_3d_lidar = liadr_r * corners_3d_lidar + np.matrix(center_lidar).T

    return corners_3d_lidar.T


class Coord_transformation(object):
    """
    coord_list=['Infrastructure_image','Infrastructure_camera','Infrastructure_lidar',
                        'world', 'Vehicle_image','Vehicle_camera','Vehicle_lidar',
                        'Vehicle_novatel']

    'Infrastructure_image' ->'Infrastructure_camera'->'Infrastructure_lidar'->'world'
                                                                                   ^
                                                                                   |
                          Vehicle_image'->'Vehicle_camera'->'Vehicle_lidar'->'Vehicle_novatel'

           Transformation                                   Function name
    infrastructure-lidar to world          ->      Coord_Infrastructure_lidar2world()
    vehicle-lidar to world                 ->      Coord_Vehicle_lidar2world()
    infrastructure-lidar to vehicle-lidar  ->      Coord_Infrastructure_lidar2Vehicle_lidar()
    world to vehicle-lidar                 ->      Coord_world2vehicel_lidar()


    Transformation equation
        a^p=a^R_b*P_b+a^P_b0
        reverse:  P_b=vers(a^R_b)a^p-vers(a^R_b)(a^P_b0)
    """

    def __init__(self, from_coord, to_coord, path_root, infra_name, veh_name):
        # self.transformer = Transformation()
        self.from_coord = from_coord
        self.to_coord = to_coord
        self.path_root = path_root
        self.infra_name = infra_name
        self.veh_name = veh_name

        # Hard code for time-compensation late fusion
        self.delta_x = None
        self.delta_y = None

    def __call__(self, point):

        path_all = {
            "path_root": self.path_root,
            "path_lidar2world": "infrastructure-side/calib/virtuallidar_to_world/" + self.infra_name + ".json",
            "path_lidar2novatel": "vehicle-side/calib/lidar_to_novatel/" + self.veh_name + ".json",
            "path_novatel2world": "vehicle-side/calib/novatel_to_world/" + self.veh_name + ".json",
        }

        rotation, translation = self.forward(self.from_coord, self.to_coord, path_all)
        return self.point_transformation(point, rotation, translation)

    def forward(self, from_coord, to_coord, path_all):
        coord_list = ["Infrastructure_lidar", "World", "Vehicle_lidar"]
        if (from_coord in coord_list) and (to_coord in coord_list):
            if from_coord == "Infrastructure_lidar" and to_coord == "World":
                rotation, translation = self.Coord_Infrastructure_lidar2world(path_all)
                return rotation, translation
            if from_coord == "Vehicle_lidar" and to_coord == "World":
                rotation, translation = self.Coord_Vehicle_lidar2world(path_all)
                return rotation, translation
            if from_coord == "Infrastructure_lidar" and to_coord == "Vehicle_lidar":
                rotation, translation = self.Coord_Infrastructure_lidar2Vehicle_lidar(path_all)
                return rotation, translation
            if from_coord == "World" and to_coord == "Vehicle_lidar":
                rotation, translation = self.Coord_world2vehicel_lidar(path_all)
                return rotation, translation
        else:
            raise ("error: wrong coordinate name")

    def rev_matrix(self, R):
        R = np.matrix(R)
        rev_R = R.I
        rev_R = np.array(rev_R)
        return rev_R

    def muilt_coord(self, rotationA2B, translationA2B, rotationB2C, translationB2C):
        rotationA2B = np.array(rotationA2B).reshape(3, 3)
        rotationB2C = np.array(rotationB2C).reshape(3, 3)
        rotation = np.dot(rotationB2C, rotationA2B)
        translationA2B = np.array(translationA2B).reshape(3, 1)
        translationB2C = np.array(translationB2C).reshape(3, 1)
        translation = np.dot(rotationB2C, translationA2B) + translationB2C
        return rotation, translation

    def reverse(self, rotation, translation):
        rev_rotation = self.rev_matrix(rotation)
        rev_translation = -np.dot(rev_rotation, translation)
        return rev_rotation, rev_translation

    def trans(self, input_point, translation, rotation):
        translation = np.array(translation).reshape(3, 1)
        rotation = np.array(rotation).reshape(3, 3)
        for point in input_point:
            output_point = np.dot(rotation, input_point.reshape(3, 1)).reshape(3) + np.array(translation).reshape(3)
        return np.array(output_point)

    def get_lidar2novatel(self, path_lidar2novatel):  # vehicle side
        lidar2novatel = self.read_json(path_lidar2novatel)
        rotation = lidar2novatel["transform"]["rotation"]
        translation = lidar2novatel["transform"]["translation"]
        return rotation, translation

    def get_novatel2world(self, path_novatel2world):  # vehicle side
        novatel2world = self.read_json(path_novatel2world)
        rotation = novatel2world["rotation"]
        translation = novatel2world["translation"]
        return rotation, translation

    def get_lidar2world(self, path_lidar2world):  # Infrastructure side, lidar to word
        lidar2world = self.read_json(path_lidar2world)
        rotation = lidar2world["rotation"]
        translation = lidar2world["translation"]
        delta_x = lidar2world["relative_error"]["delta_x"]
        delta_y = lidar2world["relative_error"]["delta_y"]
        if delta_x == "":
            delta_x = 0
        if delta_y == "":
            delta_y = 0

        return rotation, translation, delta_x, delta_y

    def read_json(self, path_json):
        with open(path_json, "r") as load_f:
            my_json = json.load(load_f)
        return my_json

    def Coord_Infrastructure_lidar2world(self, path_all):
        rotation, translation, delta_x, delta_y = self.get_lidar2world(
            os.path.join(path_all["path_root"], path_all["path_lidar2world"])
        )
        return rotation, translation

    def Coord_world2vehicel_lidar(self, path_all):
        # world to novatel
        rotation, translation = self.get_novatel2world(
            os.path.join(path_all["path_root"], path_all["path_novatel2world"])
        )
        rotationA2B, translationA2B = self.reverse(rotation, translation)
        # novatel to lidar
        rotation, translation = self.get_lidar2novatel(
            os.path.join(path_all["path_root"], path_all["path_lidar2novatel"])
        )
        rotationB2C, translationB2C = self.reverse(rotation, translation)
        new_rotationA2C, new_translationA2C = self.muilt_coord(rotationA2B, translationA2B, rotationB2C, translationB2C)
        return new_rotationA2C, new_translationA2C

    def Coord_Vehicle_lidar2world(self, path_all):
        rotationA2B, translationA2B = self.get_lidar2novatel(
            os.path.join(path_all["path_root"], path_all["path_lidar2novatel"])
        )
        rotationB2C, translationB2C = self.get_novatel2world(
            os.path.join(path_all["path_root"], path_all["path_novatel2world"])
        )
        new_rotationA2C, new_translationA2C = self.muilt_coord(rotationA2B, translationA2B, rotationB2C, translationB2C)

        return new_rotationA2C, new_translationA2C

    def Coord_Infrastructure_lidar2Vehicle_lidar(self, path_all):
        rotationA2B, translationA2B, delta_x, delta_y = self.get_lidar2world(
            os.path.join(path_all["path_root"], path_all["path_lidar2world"])
        )
        if self.delta_x is not None:
            delta_x = self.delta_x
            delta_y = self.delta_y
        self.delta_x = delta_x
        self.delta_y = delta_y

        translationA2B = translationA2B + np.array([delta_x, delta_y, 0]).reshape(3, 1)
        rotationB2C, translationB2C = self.Coord_world2vehicel_lidar(path_all)
        new_rotationA2C, new_translationA2C = self.muilt_coord(rotationA2B, translationA2B, rotationB2C, translationB2C)

        return new_rotationA2C, new_translationA2C

    def point_transformation(self, input_box, rotation, translation):
        translation = np.array(translation).reshape(3, 1)
        rotation = np.array(rotation).reshape(3, 3)
        output = []
        for box in input_box:
            if len(box) == 3:
                output.append(np.dot(rotation, box.reshape(3, 1)).reshape(3) + np.array(translation).reshape(3))
                continue
            output_point = []
            for point in box:
                output_point.append(np.dot(rotation, point.reshape(3, 1)).reshape(3) + np.array(translation).reshape(3))
            output.append(output_point)

        return np.array(output)

    def single_point_transformation(self, input_point):
        path_all = {
            "path_root": self.path_root,
            "path_lidar2world": "infrastructure-side/calib/virtuallidar_to_world/" + self.infra_name + ".json",
            "path_lidar2novatel": "vehicle-side/calib/lidar_to_novatel/" + self.veh_name + ".json",
            "path_novatel2world": "vehicle-side/calib/novatel_to_world/" + self.veh_name + ".json",
        }

        rotation, translation = self.forward(self.from_coord, self.to_coord, path_all)
        input_point = np.array(input_point).reshape(3, 1)
        translation = np.array(translation).reshape(3, 1)
        rotation = np.array(rotation).reshape(3, 3)
        output_point = np.dot(rotation, input_point).reshape(3, 1) + np.array(translation).reshape(3, 1)

        return output_point


if __name__ == "__main__":
    rotation = [
        [-0.0638033225610772, -0.9910914864003576, -0.04429948490729328],
        [-0.2102873406178483, 0.043997692433495696, -0.7987692871343754],
        [0.97575114561348, -0.06031492538699515, -0.17158543199893228],
    ]
    translation = [[-5.779144404715124], [6.037615758600886], [1.0636424034755758]]
    calib = Coord_transformation(rotation, translation)
    print("Init: ", calib.rotation, calib.translation)

    calib_inv = calib.inv()
    print("Inverse: ", calib_inv.rotation, calib_inv.translation)

    rotation_other = [
        [0.854463098610578, -0.5195105091837793, 0.0012102751176149926],
        [0.5195000561482762, 0.8544244218454334, -0.0088276425335725],
        [0.0035518987605347592, 0.008171634487169012, 0.9999599188996214],
    ]
    translation_other = [[3390.138583273976], [2087.3119082041085], [20.66834816604844]]
    calib_other = Coord_transformation(rotation_other, translation_other)
    calib_mul = calib.matmul(calib_other)
    print("Matmul: ", calib_mul.rotation, calib_mul.translation)
