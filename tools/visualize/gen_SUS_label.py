import os
import json
import argparse
import pandas as pd


def read_json(path_json):
    with open(path_json, "r") as load_f:
        my_json = json.load(load_f)
    return my_json


def write_json(path_json, new_dict):
    with open(path_json, "w") as f:
        json.dump(new_dict, f)


def gen_sus_label_from_dair_v2x(root_path, output_path):
    """
        Generate SUS visualization file for DAIR-V2X label.(Take vehicle-side for example.)

        Args:
            root_path: V2X-Seq-SPD/
            output_path： SUSTechPOINTS/data/output/
            
        Returns:
            None
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path + '/label')
        os.makedirs(output_path + '/lidar')
        os.makedirs(output_path + '/calib')
        os.makedirs(output_path + '/camera/front')
        os.makedirs(output_path + '/camera/left')
        os.makedirs(output_path + '/camera/right')

    veh_label_name = 'lidar'

    veh_img_path = os.path.join(root_path, 'vehicle-side/image')
    veh_pt_path = os.path.join(root_path, 'vehicle-side/velodyne')
    veh_label_path = os.path.join(root_path, 'vehicle-side/label', veh_label_name)

    list_input_file = os.listdir(veh_label_path)
    for file_name in list_input_file:
        veh_frame_id = file_name.split('.')[0]

        os.system("cp %s/%s.jpg %s/camera/front/%s.jpg" % (
            veh_img_path, veh_frame_id, output_path, veh_frame_id))
        os.system("cp %s/%s.pcd %s/lidar/%s.pcd" % (
            veh_pt_path, veh_frame_id, output_path, veh_frame_id))

        cur_veh_label_path = os.path.join(veh_label_path, file_name)

        output_label_file_path = output_path + '/label/' + file_name
        data_json = read_json(cur_veh_label_path)
        lidar_3d_list = []
        for i in data_json:
            lidar_3d_data = {}
            lidar_3d_data["obj_id"] = str(i["track_id"])
            lidar_3d_data["obj_type"] = str(i["type"])
            lidar_3d_data["psr"] = {}
            lidar_3d_data["psr"]["position"] = {}
            lidar_3d_data["psr"]["position"]["x"] = float(i["3d_location"]["x"])
            lidar_3d_data["psr"]["position"]["y"] = float(i["3d_location"]["y"])
            lidar_3d_data["psr"]["position"]["z"] = float(i["3d_location"]["z"])
            lidar_3d_data["psr"]["rotation"] = {}
            lidar_3d_data["psr"]["rotation"]["x"] = 0.0
            lidar_3d_data["psr"]["rotation"]["y"] = 0.0
            lidar_3d_data["psr"]["rotation"]["z"] = float(i["rotation"])
            lidar_3d_data["psr"]["scale"] = {}
            lidar_3d_data["psr"]["scale"]["x"] = float(i["3d_dimensions"]["l"])
            lidar_3d_data["psr"]["scale"]["y"] = float(i["3d_dimensions"]["w"])
            lidar_3d_data["psr"]["scale"]["z"] = float(i["3d_dimensions"]["h"])
            # print(lidar_3d_data)
            lidar_3d_list.append(lidar_3d_data)
        write_json(output_label_file_path, lidar_3d_list)


def gen_sus_from_kitti_file(side_flag, only_gen_label, dair_datasets_path, input_file_path, output_path):
    """
        Generate SUS visualization file for DAIR-V2X kitti label

        Args:
            side_flag: 'coop','veh','inf', 'i2v'
            dair_datasets_path: V2X-Seq-SPD/
            input_path: kitti_label_file (such as: cooperative-vehicle-infrastructure/infrastructure-side/validation/0003/label_02/0003.txt)            
            output_path: SUSTechPOINTS/data/output/

        Returns:
            None
    """

    if os.path.exists(output_path):
        os.system('rm -rf %s' % (output_path))

    output_path_label = os.path.join(output_path, 'label')
    os.makedirs(output_path_label)

    if side_flag == 'i2v':
        coop_data_info_file_path = os.path.join(dair_datasets_path, 'cooperative/data_info.json')
        with open(coop_data_info_file_path) as f:
            coop_data_info = json.load(f)
        frameid_i2v_dict = {}
        for coop_data in coop_data_info:
            frameid_i2v_dict[coop_data['infrastructure_frame']] = coop_data['vehicle_frame']

    if not only_gen_label:
        output_path_lidar = os.path.join(output_path, 'lidar')
        output_path_camera_front = os.path.join(output_path, 'camera/front')
        os.makedirs(output_path_lidar)
        os.makedirs(output_path_camera_front)

        if side_flag == 'inf':
            img_path = os.path.join(dair_datasets_path, 'infrastructure-side/image')
            velodyne_path = os.path.join(dair_datasets_path, 'infrastructure-side/velodyne')
        elif side_flag == 'veh' or side_flag == 'coop':
            img_path = os.path.join(dair_datasets_path, 'vehicle-side/image')
            velodyne_path = os.path.join(dair_datasets_path, 'vehicle-side/velodyne')
        elif side_flag == 'i2v':
            img_path = os.path.join(dair_datasets_path, 'infrastructure-side/image')
            velodyne_path = os.path.join(dair_datasets_path, 'vehicle-side/velodyne')

    if side_flag == 'coop':
        names = ['frame', 'type', 'track_id', 'truncated', 'occlude', 'alpha', 'bbox-left', 'bbox-top',
                 'bbox-right', 'bbox-bottom', 'h', 'w', 'l', 'camera_bottom_center_x', 'camera_bottom_center_y',
                 'camera_bottom_center_z', 'rotation_y', 'lidar_center_x', 'lidar_center_y', 'lidar_center_z',
                 'rotation_z', 'pointcloud_timestamp', 'score_dtc', 'score_tracking', 'token', 'from_side',
                 'veh_pointcloud_timestamp', 'inf_pointcloud_timestamp', 'veh_frame_id', 'inf_frame_id', 'veh_track_id',
                 'inf_track_id', 'veh_dtc_score', 'inf_dtc_score', 'veh_track_score', 'inf_track_score', 'veh_tocken', 'inf_tocken'
                 ]
    else:
        names = ['frame', 'type', 'track_id', 'truncated', 'occlude', 'alpha', 'bbox-left', 'bbox-top',
                 'bbox-right', 'bbox-bottom', 'h', 'w', 'l', 'camera_bottom_center_x', 'camera_bottom_center_y',
                 'camera_bottom_center_z', 'rotation_y', 'lidar_center_x', 'lidar_center_y', 'lidar_center_z',
                 'rotation_z', 'pointcloud_timestamp', 'score_dtc', 'score_tracking', 'token'
                 ]

    df = pd.read_csv(input_file_path, sep=' ', header=None, names=names)
    for frame in list(set(df['frame'])):
        from_frame_id = '%06d' % int(frame)
        to_frame_id = from_frame_id

        if side_flag == 'i2v':
            to_frame_id = frameid_i2v_dict[from_frame_id]

        if not only_gen_label:
            # lidar/camera
            os.system("cp %s/%s.jpg %s/%s.jpg" % (
                img_path, from_frame_id, output_path_camera_front, to_frame_id))
            os.system("cp %s/%s.pcd %s/%s.pcd" % (
                velodyne_path, to_frame_id, output_path_lidar, to_frame_id))

            # label
        output_file_path = output_path_label + '/' + to_frame_id + '.json'
        m = df[df['frame'] == frame]
        lidar_3d_list = []
        for i, row in m.iterrows():
            lidar_3d_data = {}

            lidar_3d_data["obj_id"] = str(int(row['track_id'])).zfill(6)
            lidar_3d_data["obj_type"] = row['type']
            if side_flag == 'coop':
                lidar_3d_data["obj_type"] = row['type'] + ' ' + row['from_side']

            lidar_3d_data["psr"] = {}
            lidar_3d_data["psr"]["position"] = {}
            lidar_3d_data["psr"]["position"]["x"] = float(row['lidar_center_x'])
            lidar_3d_data["psr"]["position"]["y"] = float(row['lidar_center_y'])
            lidar_3d_data["psr"]["position"]["z"] = float(row['lidar_center_z'])
            lidar_3d_data["psr"]["rotation"] = {}
            lidar_3d_data["psr"]["rotation"]["x"] = 0.0
            lidar_3d_data["psr"]["rotation"]["y"] = 0.0
            lidar_3d_data["psr"]["rotation"]["z"] = float(row['rotation_z'])
            lidar_3d_data["psr"]["scale"] = {}
            lidar_3d_data["psr"]["scale"]["x"] = float(row['l'])
            lidar_3d_data["psr"]["scale"]["y"] = float(row['w'])
            lidar_3d_data["psr"]["scale"]["z"] = float(row['h'])
            # print(lidar_3d_data)
            lidar_3d_list.append(lidar_3d_data)
        write_json(output_file_path, lidar_3d_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("3d visualization.")
    parser.add_argument('--dair_datasets_path', type=str, default='V2X-Seq-SPD')
    parser.add_argument('--input_file_path', type=str, default='')
    parser.add_argument('--output_path', type=str, default='')
    parser.add_argument('--side_flag', type=str, default='coop')  # 'veh','inf','coop','i2v'
    parser.add_argument('--only_gen_label', action="store_true")

    args = parser.parse_args()
    print('begin visual.')

    # visualization
    # #veh
    # args.output_path = 'visualize/coop_seq0000'      
    # gen_sus_label_from_dair_v2x(args.dair_datasets_path,args.output_path)

    # kitti file
    args.side_flag = "coop"  # 'veh','inf','coop','i2v'
    args.only_gen_label = True
    args.input_file_path = 'kitti/cooperative-vehicle-infrastructure/cooperative/training/0000/label_02/0000.txt'
    args.output_path = 'visualize/coop_seq0000'
    gen_sus_from_kitti_file(args.side_flag, args.only_gen_label, args.dair_datasets_path, args.input_file_path, args.output_path)
