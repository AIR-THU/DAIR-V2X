## Introduction
We choose the PointPillars as the infrastructure 3D detector and vehicle 3D detector respectively.
We use the late fusion to fuse the infrastruture and vehicle information.
We apply our Time Compensation Late Fusion (TCLF) to alleviate the temporal asynchrony problem.
We train and inference the two 3D detectors on DAIR-V2X-C with MMDetection3D Framework.
We inference the whole VIC3D detector and evaluate detection performance with our OpenDAIRV2X Framework.

## Results and models
We provide the evaluation results here.
Note that the evaluation results are higher than the results reported in our CVPR2022 Paper.

| Modality  | Fusion  | Model      | Dataset   | AP-3D (IoU=0.5)  |        |        |         | AP-BEV (IoU=0.5)  |       |        |         |   AB   | Model Download |
| :-------: | :-----: | :--------: | :-------: | :----: | :----: | :----: | :-----: | :-----: | :---: | :----: | :-----: | :----: | :----:                |
|           |         |            |           | Overall | 0-30m | 30-50m | 50-100m | Overall | 0-30m | 30-50m | 50-100m |        | [inf-model](https://drive.google.com/file/d/1BO5dbqmLjC3gTjvQTyfEjhIikFz2P_Om/view?usp=sharing) & [veh-model](https://drive.google.com/file/d/1tY1sqQGGSaRoA8KDeIQPjcUZ20I82wTK/view?usp=sharing)    
|Pointcloud | VehOnly | PointPillars | VIC-Sync | 48.06  | 47.62 | 63.51  | 44.37   | 52.24   | 30.55 | 66.03  |  48.36  | 0      | 
|           | InfOnly | PointPillars | VIC-Sync | 17.58  | 23.00 | 13.96  | 9.17    | 27.26   | 29.07 | 23.92  | 26.64   | 478.61      |        
|       | Late-Fusion | PointPillars | VIC-Sync | 56.06  | 55.69 | 68.44  | 53.60   | 62.06   | 61.52 | 72.53  | 60.57   | 478.61 |                         
|       | Late-Fusion | PointPillars |VIC-Async-1| 53.80 | 53.26 | 67.40  | 50.85   | 59.94   | 59.51 | 71.45  | 57.74   | 341.08 | 
|       | Late-Fusion | PointPillars |VIC-Async-2| 52.43 | 51.13 | 67.09  | 49.86   | 58.10   | 57.23 | 70.86  | 55.78   | 478.01 |
|       | TCLF        | PointPillars |VIC-Async-1| 54.09 | 53.43 | 67.50  | 51.38   | 60.19   | 59.52 | 71.52  | 58.31   | 907.64 | 
|       | TCLF        | PointPillars |VIC-Async-2| 53.37 | 52.41 | 67.33  | 50.87   | 59.17   | 58.25 | 71.20  | 57.43   | 897.91 |

## Training & Evaluation

### Data Preparation
#### Download data and organise as follows
```
# For DAIR-V2X-C Dataset located at ${DAIR-V2X-C_DATASET_ROOT}
└── cooperative-vehicle-infrastructure       <-- DAIR-V2X-C
    └──── infrastructure-side                         <-- DAIR-V2X-C-I   
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label    
       └────  data_info.json    
    └──── vehicle-side                                         <-- DAIR-V2X-C-V  
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label
       └───── data_info.json
    └──── cooperative 
       ├───── label_world
       └───── data_info.json              
```

#### Create a symlink to the dataset root
```
cd ${dair-v2x_root}/dair-v2x
mkdir ./data/DAIR-V2X
ln -s ${DAIR-V2X-C_DATASET_ROOT}/cooperative-vehicle-infrastructure ${dair-v2x_root}/dair-v2x/data/DAIR-V2X
```

#### Create Kitti-format data (Option for model training)

Data creation should be under the gpu environment.
```commandline
# Kitti Format
cd ${dair-v2x_root}/dair-v2x
python tools/dataset_converter/dair2kitti.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/infrastructure-side \
    --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/infrastructure-side \
    --split-path ./data/split_datas/cooperative-split-data.json \
    --label-type lidar --sensor-view infrastructure --no-classmerge
python tools/dataset_converter/dair2kitti.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side \
    --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side \
    --split-path ./data/split_datas/cooperative-split-data.json \
    --label-type lidar --sensor-view vehicle --no-classmerge
```
In the end, the data and info files should be organized as follows
```
└── cooperative-vehicle-infrastructure   <-- DAIR-V2X-C
    └──── infrastructure-side              <-- DAIR-V2X-C-I
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label
       ├───── data_info.json
       ├───── ImageSets
       └────  training
          ├───── image_2
          ├───── velodyne
          ├───── label_2
          └───── calib
       └──── testing   
    ├───── vehicle-side                            <-- DAIR-V2X-C-V  
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label
       ├───── data_info.json
       ├───── ImageSets
       └────  training
          ├───── image_2
          ├───── velodyne
          ├───── label_2
          └───── calib
    └────  cooperative 
       ├───── label_world
       └───── data_info.json
```

* VIC-Sync Dataset. VIC-Sync dataset is extracted from DAIR-V2X-C, which is composed of 9311 pairs of infrastructure and vehicle frames as well as their cooperative annotations as ground truth.
  We split VIC-Sync dataset to train/valid/test part as 5:2:3 respectively. 
  Please refer [split data](../../../data/split_datas/cooperative-split-data.json) for the splitting file. 
  
* VIC-Async Dataset. To simulate the temporal asynchrony phenomenon, 
  we replace each infrastructure frame in the VIC-Sync dataset with the infrastructure frame, 
  which is the k-th frame previous to the original infrastructure frame to construct the VIC-Async-k dataset.
  Note that the k-th frame previous to some frames may not exist.
  In this case, we directly replace it with the current frame.


### Training
* Implementation Framework. 
  We directly use MMDetection3D (v0.17.1) to train the infrastructure 3D detector and vehicle 3D detector.
* Infrastructure detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/cooperative-vehicle-infrastructure/infrastructure-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_i.py](trainval_config_i.py)
  
* Vehicle detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_v.py](trainval_config_v.py)
  
### Evaluation

Download following checkpoints and place them in this directory.
* [vic3d_latefusion_inf_pointpillars](https://drive.google.com/file/d/1BO5dbqmLjC3gTjvQTyfEjhIikFz2P_Om/view?usp=sharing)
* [vic3d_latefusion_veh_pointpillars](https://drive.google.com/file/d/1tY1sqQGGSaRoA8KDeIQPjcUZ20I82wTK/view?usp=sharing)    

Then use the following commands to get the evaluation results.
```
# An example to get the TCLF evaluation results within [0, 100]m range on VIC-Async-2 dataset
# bash scripts/eval_lidar_late_fusion_pointpillars.sh [YOUR_CUDA_DEVICE] [FUSION_METHOD] [DELAY_K] [EXTEND_RANGE_START] [EXTEND_RANGE_END] [TIME_COMPENSATION]
cd ${dair-v2x_root}/dair-v2x/v2x
bash scripts/eval_lidar_late_fusion_pointpillars.sh 0 late_fusion 2 0 100
```
* FUSION_METHOD candidates: [veh_only, inf_only, late_fusion].
* DELAY_K candidates: [0, 1, 2]. 0 denotes VIC-Sync dataset, 1 denotes VIC-Async-1 dataset, 
  2 denotes VIC-Async-2 dataset.
* [EXTEND_RANGE_START, EXTEND_RANGE_END] candidates: [[0, 100], [0, 30], [30, 50], [50, 100]].
* TIME_COMPENSATION candidates: [, --no-comp]. Empty denotes that we use time compensation to alleviate the temporal asyncrony problem.