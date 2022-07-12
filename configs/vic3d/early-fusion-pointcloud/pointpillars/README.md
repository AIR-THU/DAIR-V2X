# Early Fusion

##  Introduction

We implement early fusion for VIC3D Detection with PointPillars and provide the results and checkpoints on VIC-Sync datasets and VIC-Async-1. 

##  Results and models

| Modality   | Fusion       | Model        | Dataset     | Overall(AP 3D Iou = 0.5) | 0-30m(AP 3D Iou = 0.5) | 30-50m(AP 3D Iou = 0.5) | 50-100m(AP 3D Iou = 0.5) | Overall(AP BEV Iou = 0.5) | 0-30m(AP BEV Iou = 0.5) | 30-50m(AP BEV Iou = 0.5) | 50-100m(AP BEV Iou = 0.5) | AB(Byte)   | Download                                                     |
| ---------- | ------------ | ------------ | ----------- | ------------------------ | ---------------------- | ----------------------- | ------------------------ | ------------------------- | ----------------------- | ------------------------ | ------------------------- | ---------- | ------------------------------------------------------------ |
| Pointcloud | Early Fusion | PointPillars | VIC-Sync    | 62.61                    | 64.82                  | 68.68                   | 56.57                    | 68.91                     | 68.92                   | 73.64                    | 65.66                     | 1382275.75 | [model](https://drive.google.com/file/d/1mo8o1iIZ2fQHYBkpfmjyMnCqYKs3wQk7/view?usp=sharing) |
| Pointcloud | Early Fusion | PointPillars | VIC-Async-1 | 57.35                    | 57.92                  | 66.23                   | 51.70                    | 64.06                     | 62.44                   | 71.42                    | 61.16                     | 1362216.0  |                                                              |

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

#### Create vic3d-early-fusion data

1. Copy "data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side" folder and rename it as "vic3d-early-fusion-training". 

    ```
    cp -r data/DAIR-V2X/cooperative-vehicle-infrastructure/vehicle-side data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training
    ```

2. Convert cooperative label from world coordinate system to vehicle LIDAR system.

    ```
    cd ${dair-v2x_root}/dair-v2x
    rm -r ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/label/lidar
    python tools/dataset_converter/label_world2v.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure \ 
        --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/label/lidar
    ```

3. Convert point cloud data from infrastructure coordinate system to vehicle coordinate system.
    ```
    python tools/dataset_converter/point_cloud_i2v.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure \
        --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne/lidar_i2v
    ```

4. Concate converted infrastructure-side point cloud data with vehicle-side point cloud data.
    ```
    python tools/dataset_converter/concatenate_pcd2bin.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure \
        --i2v-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne/lidar_i2v \
        --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne-concated
    rm -r ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne
    mv ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne-concated \
        ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/velodyne
    ```
5. Convert vehicle-side data_info.json to cooperative data_info.json
    ```
    python tools/dataset_converter/get_fusion_data_info.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure \ --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training
    rm ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/data_info.json
    mv ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/fusion_data_info.json ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training/data_info.json
    ```
#### Create Kitti-format data (Option for model training)

Data creation should be under the gpu environment.

    # Kitti Format
    cd ${dair-v2x_root}/dair-v2x
    python tools/dataset_converter/dair2kitti.py --source-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training \
        --target-root ./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training \
        --split-path ./data/split_datas/cooperative-split-data.json \
        --label-type lidar --sensor-view cooperative --no-classmerge


In the end, the data and info files should be organized as follows
```
└── cooperative-vehicle-infrastructure   <-- DAIR-V2X-C
    └──── infrastructure-side                      <-- DAIR-V2X-C-I
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label
       └───── data_info.json 
    └───── vehicle-side                                <-- DAIR-V2X-C-V  
       ├───── image
       ├───── velodyne
       ├───── calib
       ├───── label
       └───── data_info.json
    └────  cooperative 
       ├───── label_world
       └───── data_info.json
    └────  vic3d-early-fusion-training
       ├───── data_info.json
       ├───── ImageSets
       └───── training
          ├───── image_2
          ├───── velodyne
          ├───── label_2
          └───── calib
```

### Training

* Implementation Framework. 
  We directly use MMDetection3D (v0.17.1) to train the 3D detector.
* Detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/cooperative-vehicle-infrastructure/vic3d-early-fusion-training" into specific training format.
  Then we train the PointPillars with configure file [trainval_config.py](trainval_config.py)
### Evaluation

Download following checkpoints and place them in this directory.
* [vic3d_earlyfusion_pointpillars](https://drive.google.com/file/d/1mo8o1iIZ2fQHYBkpfmjyMnCqYKs3wQk7/view?usp=sharing)

Then use the following commands to get the evaluation results.

    # An example to get the early fusion evaluation results within [0, 100]m range on VIC-Async-1 dataset
    # bash scripts/eval_lidar_early_fusion_pointpillars.sh [YOUR_CUDA_DEVICE] [FUSION_METHOD] [DELAY_K] [EXTEND_RANGE_START] [EXTEND_RANGE_END] 
    cd ${dair-v2x_root}/dair-v2x/v2x
    bash scripts/eval_lidar_early_fusion_pointpillars.sh 0 early_fusion 1 0 100

* FUSION_METHOD candidates: [early_fusion].
* DELAY_K candidates: [0, 1]. 0 denotes VIC-Sync dataset, 1 denotes VIC-Async-1 dataset.
* [EXTEND_RANGE_START, EXTEND_RANGE_END] candidates: [[0, 100], [0, 30], [30, 50], [50, 100]].