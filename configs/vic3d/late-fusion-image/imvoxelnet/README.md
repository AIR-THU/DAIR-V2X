# ImvoxelNet

## Introduction

We implement ImvoxelNet and provide the results and checkpoints on VIC-Sync datasets with MMDetection3D.

## Results and models

| Modality | Fusion      | Model      | Dataset  |         | AP-3D(IoU=0.5) |        |         |         | AP-BEV(IoU=0.5) |        |         | AB(Byte)    | Download                                                     |
| -------- | ----------- | ---------- | -------- | ------- | ------------- | ------ | ------- | ------- | --------------- | ------ | ------- | ------ | ------------------------------------------------------------ |
|          |             |            |          | Overall | 0-30m         | 30-50m | 50-100m | Overall | 0-30m           | 30-50m | 50-100m |   |                                                              |
| Image    | Veh Only   | ImvoxelNet | VIC-Sync |  9.13   | 19.06         | 5.23  | 0.41   | 10.96   | 21.93           | 7.28  | 0.78   | 0      | [model_v](https://drive.google.com/file/d/1dNupazp9t2D6mN8cs1ER8zuf3j9ZHNd6/view?usp=sharing) |
| Image    | Inf Only   | ImvoxelNet | VIC-Sync | 14.02   | 20.56         | 8.89  | 10.57   | 22.10   | 27.33           | 17.45  | 18.92   | 309.38 | [model_i](https://drive.google.com/file/d/1F0QSlsGQhtMd3Q66CcXgQJKZptERYhhk/view?usp=sharing) |
| Image    | Late Fusion | ImvoxelNet | VIC-Sync | 18.77   | 33.47         | 9.43  | 8.62    | 24.85   | 39.49           | 14.68  | 14.96   | 309.38 |        |

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


### Training
* Implementation Framework. 
  We directly use MMDetection3D (v0.17.1) to train the infrastructure 3D detector and vehicle 3D detector.
* Infrastructure detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/cooperative-vehicle-infrastructure/infrastructure-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_i.py](./trainval_config_i.py)
  
* Vehicle detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_v.py](./trainval_config_v.py)
  
### Evaluation

Download following checkpoints and place them in this directory.
* [vic3d_latefusion_inf_imvoxelnet](https://drive.google.com/file/d/1F0QSlsGQhtMd3Q66CcXgQJKZptERYhhk/view?usp=sharing)
* [vic3d_latefusion_veh_imvoxelnet](https://drive.google.com/file/d/1dNupazp9t2D6mN8cs1ER8zuf3j9ZHNd6/view?usp=sharing)    

Then use the following commands to get the evaluation results.
```
# An example to get the late fusion evaluation results within [0, 100]m range on VIC-Sync dataset
# bash scripts/eval_camera_late_fusion_imvoxelnet.sh [YOUR_CUDA_DEVICE] [FUSION_METHOD] [DELAY_K] [EXTEND_RANGE_START] [EXTEND_RANGE_END] [TIME_COMPENSATION]
cd ${dair-v2x_root}/dair-v2x/v2x
bash scripts/eval_camera_late_fusion_imvoxelnet.sh 0 late_fusion 0 0 100 --no-comp
```
* FUSION_METHOD candidates: [veh_only, inf_only, late_fusion].
* DELAY_K candidates: [0, 1, 2]. 0 denotes VIC-Sync dataset, 1 denotes VIC-Async-1 dataset, 
  2 denotes VIC-Async-2 dataset.
* [EXTEND_RANGE_START, EXTEND_RANGE_END] candidates: [[0, 100], [0, 30], [30, 50], [50, 100]].
* TIME_COMPENSATION candidates: [, --no-comp]. Empty denotes that we use time compensation to alleviate the temporal asyncrony problem.