# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com

import yaml, numpy as np, os
from easydict import EasyDict as edict

# from AB3DMOT_libs.model_multi import AB3DMOT_multi

# from AB3DMOT_libs.kitti_oxts import load_oxts
# from AB3DMOT_libs.kitti_calib import Calibration
# from AB3DMOT_libs.nuScenes_split import get_split
from xinshuo_io import mkdir_if_missing, is_path_exists, fileparts, load_list_from_folder
from xinshuo_miscellaneous import merge_listoflist
from AB3DMOT_libs.model import AB3DMOT_custom


def Config(filename):
    listfile1 = open(filename, 'r')
    listfile2 = open(filename, 'r')
    cfg = edict(yaml.safe_load(listfile1))
    settings_show = listfile2.read().splitlines()

    listfile1.close()
    listfile2.close()

    return cfg, settings_show


def get_subfolder_seq(dataset, split, split_data_path):
    

    # dataset setting
    file_path = os.path.dirname(os.path.realpath(__file__))

    if dataset == 'KITTI':  # KITTI
        det_id2str = {0: 'Trafficcone', 1: 'Pedestrian', 2: 'Car', 3: 'Cyclist', 4: 'Van', 5: 'Truck', 6: 'Bus',
                      7: 'Tricyclist', 8: 'Motorcyclist', 9: 'Barrowlist'}

        if split == 'val':
            subfolder = 'validation'
        elif split == 'test':
            subfolder = 'testing'
        else:
            subfolder = 'training'

        hw = {'image': (1920, 1080), 'lidar': (720, 1920)}

        import json
        with open(split_data_path,'r') as fp:
            split_data = json.load(fp)
        
        seq_eval = split_data['batch_split'][split]     

        data_root = os.path.join(file_path, '../../../data/V2X-Seq-SPD-KITTI')  # path containing the KITTI root
        
    else:
        assert False, 'error, %s dataset is not supported' % dataset

    return subfolder, det_id2str, hw, seq_eval, data_root


def get_threshold(dataset, det_name):
    # used for visualization only as we want to remove some false positives, also can be
    # used for KITTI 2D MOT evaluation which uses a single operating point
    # obtained by observing the threshold achieving the highest MOTA on the validation set

    if dataset == 'KITTI':
        # if det_name == 'pointrcnn':
        if det_name:
            return {'Car': 3.240738, 'Pedestrian': 2.683133, 'Cyclist': 3.645319}
        else:
            assert False, 'error, detection method not supported for getting threshold' % det_name
    elif dataset == 'nuScenes':
        if det_name == 'megvii':
            return {'Car': 0.262545, 'Pedestrian': 0.217600, 'Truck': 0.294967, 'Trailer': 0.292775,
                    'Bus': 0.440060, 'Motorcycle': 0.314693, 'Bicycle': 0.284720}
        if det_name == 'centerpoint':
            return {'Car': 0.269231, 'Pedestrian': 0.410000, 'Truck': 0.300000, 'Trailer': 0.372632,
                    'Bus': 0.430000, 'Motorcycle': 0.368667, 'Bicycle': 0.394146}
        else:
            assert False, 'error, detection method not supported for getting threshold' % det_name
    else:
        assert False, 'error, dataset %s not supported for getting threshold' % dataset


def initialize(cfg, data_root, seq_dets, subfolder, seq_name, cat, ID_start, log_file):
    # initiate the tracker
    if cfg.num_hypo > 1:
        # tracker = AB3DMOT_multi(cfg, cat, calib=None, oxts=None, img_dir=None, vis_dir=None, hw=None, log=log_file,
        #                         ID_init=ID_start)
        assert False, 'error'
    elif cfg.num_hypo == 1:
        tracker = AB3DMOT_custom(cfg, cat, calib=None, oxts=None, img_dir=None, vis_dir=None, hw=None, log=log_file, ID_init=ID_start)
    else:
        assert False, 'error'

    # compute the min/max frame
    frame_list = list(seq_dets[:, 0])
    frame_list = list(set(frame_list))

    return tracker, frame_list


def find_all_frames(root_dir, subset, data_suffix, seq_list):
    # warm up to find union of all frames from results of all categories in all sequences
    # finding the union is important because there might be some sequences with only cars while
    # some other sequences only have pedestrians, so we may miss some results if mainly looking
    # at one single category
    # return a dictionary with each key correspondes to the list of frame ID

    # loop through every sequence
    frame_dict = dict()
    for seq_tmp in seq_list:
        frame_all = list()

        # find all frame indexes for each category
        for subset_tmp in subset:
            data_dir = os.path.join(root_dir, subset_tmp, 'trk_withid' + data_suffix, seq_tmp)  # pointrcnn_ped
            if not is_path_exists(data_dir):
                print('%s dir not exist' % data_dir)
                # assert False, 'error'
                continue

            # extract frame string from this category
            frame_list, _ = load_list_from_folder(data_dir)
            frame_list = [fileparts(frame_tmp)[1] for frame_tmp in frame_list]
            frame_all.append(frame_list)

        # merge frame indexes from all categories
        
        try:
            frame_all = merge_listoflist(frame_all, unique=True)
        except:
            frame_all = list()
        frame_dict[seq_tmp] = frame_all

    return frame_dict
