# ImvoxelNet

## Introduction

We implement ImvoxelNet and provide the results and checkpoints on VIC-Sync-SPD datasets with MMDetection3D.

## Results and models

| Modality | Fusion      | Model       | Dataset      | AP 3D (Iou=0.5) | AP BEV (Iou=0.5) | AB(Byte) | Download                                                                                        |
|----------|-------------|-------------|--------------|-----------------|------------------|----------|-------------------------------------------------------------------------------------------------|
| Image    | Veh Only    | ImvoxelNet  | VIC-Sync-SPD | 8.55            | 10.32            |          | [veh-model](https://drive.google.com/file/d/1eZWsG3VzMuC8swYfVveM3Zg3fcGR6IvN/view?usp=sharing) |
| Image    | Late Fusion | ImvoxelNet  | VIC-Sync-SPD | 17.31           | 22.53            | 3300     | [inf-model](https://drive.google.com/file/d/1XntybUfSXQMZgiZnT7INRYPLBuHXT-Lv/view?usp=sharing) |

---

## Detection

### Data Preparation

**a. Download data and organise as follows**

Download SPD dataset [here](https://thudair.baai.ac.cn/coop-forecast) and organize as follows:

```
# For SPD Dataset located at ${SPD_DATASET_ROOT}
V2X-Seq-SPD/ 
    └──  infrastructure-side            # Infrastructure-side data
        ├── image		        
            ├── {id}.jpg
        ├── velodyne                    
            ├── {id}.pcd               
        ├── calib                     
            ├── camera_intrinsic        # Camera intrinsic parameter       
                ├── {id}.json         
            ├── virtuallidar_to_world   # Extrinsic parameter from virtual LiDAR coordinate system to world coordinate system
                ├── {id}.json          
            ├── virtuallidar_to_camera  # Extrinsic parameter from virtual LiDAR coordinate system to camera coordinate system
                ├── {id}.json          
        ├── label			
            ├── camera                  # Labeles in infrastructure virtual LiDAR coordinate system fitting objects in image with image camptured timestamp
                ├── {id}.json
            ├── virtuallidar            # Labeles in infrastructure virtual LiDAR coordinate system fitting objects in point cloud with point cloud captured timestamp
                ├── {id}.json
        └── data_info.json              # More detailed information for each infrastructure-side frame
    └── vehicle-side                    # Vehicle-side data
        ├── image		        
            ├── {id}.jpg
        ├── velodyne                 
            ├── {id}.pcd               
        ├── calib                     
            ├── camera_intrinsic        # Camera intrinsic parameter   
                ├── {id}.json
            ├── lidar_to_camera         # extrinsic parameter from LiDAR coordinate system to camera coordinate system 
                ├── {id}.json
            ├── lidar_to_novatel        # extrinsic parameter from LiDAR coordinate system to NovAtel coordinate system
                ├── {id}.json
            ├── novatel_to_world        # location in the world coordinate system
                ├── {id}.json
        ├── label			
            ├── camera                  # Labeles in vehicle LiDAR coordinate system fitting objects in image with image camptured timestamp
                ├── {id}.json
            ├── lidar                   # Labeles in vehicle LiDAR coordinate system fitting objects in point cloud with point cloud captured timestamp
                ├── {id}.json
        └── data_info.json              # More detailed information for each vehicle-side frame
    └── cooperative                     # Coopetative-view files
        ├── label                       # Vehicle-infrastructure cooperative (VIC) annotation files. Labeles in vehicle LiDAR coordinate system with the vehicle point cloud timestamp
            ├── {id}.json                
        └── data_info.json              # More detailed information for vehicle-infrastructure cooperative frame pair
    └── maps                            # HD Maps for each intersection
```

**b. Create a symlink to the dataset root**

```bash
cd ${DAIR-V2X_ROOT}
ln -s ${SPD_DATASET_ROOT} ./data/V2X-Seq-SPD
```

**c. Create Kitti-format data (Option for model training)**

Data creation should be under the gpu environment.

```bash
cd ${DAIR-V2X_ROOT}
python tools/dataset_converter/spd2kitti_detection/dair2kitti.py \
   --source-root ./data/V2X-Seq-SPD/infrastructure-side \
   --target-root ./data/V2X-Seq-SPD/infrastructure-side \
   --split-path ./data/split_datas/cooperative-split-data-spd.json \
   --label-type lidar \
   --sensor-view infrastructure \
   --no-classmerge
python tools/dataset_converter/spd2kitti_detection/dair2kitti.py \
   --source-root ./data/V2X-Seq-SPD/vehicle-side \
   --target-root ./data/V2X-Seq-SPD/vehicle-side \
   --split-path ./data/split_datas/cooperative-split-data-spd.json \
   --label-type lidar \
   --sensor-view vehicle \
   --no-classmerge
```

In the end, the data and info files should be organized as follows:

```
V2X-Seq-SPD/     
    └──── infrastructure-side              
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
    ├───── vehicle-side                     
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
    └────  cooperative 
       ├───── label_world
       └───── data_info.json
```

* VIC-Sync-SPD Dataset. VIC-Sync-SPD dataset is extracted from V2X-Seq-SPD, which is composed of 15,371 pairs of infrastructure and vehicle frames as well as their cooperative annotations as ground truth.
  We split V2X-Seq-SPD dataset to train/valid/test part as 5:2:3 respectively. 
  Please refer [split data](../../../data/split_datas/cooperative-split-data-spd.json) for the splitting file. 

### Training & Evaluation

#### Training

* Implementation Framework. We directly use MMDetection3D (v0.17.1) to train the infrastructure 3D detector and vehicle 3D detector.

* Infrastructure detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/V2X-Seq-SPD/infrastructure-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_i.py](./trainval_config_i.py)
  
* Vehicle detector training details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/V2X-Seq-SPD/vehicle-side" into specific training format.
  Then we train the PointPillars with configure file [trainval_config_v.py](./trainval_config_v.py)
  
#### Evaluation

**a. Detection Checkpoint Preparation**

Download checkpoints of ImvoxelNet trained on V2X-Seq-SPD datasets with mmdetection3d from Google drive: [inf-model](https://drive.google.com/file/d/1XntybUfSXQMZgiZnT7INRYPLBuHXT-Lv/view?usp=sharing) & [veh-model](https://drive.google.com/file/d/1eZWsG3VzMuC8swYfVveM3Zg3fcGR6IvN/view?usp=sharing). 

Put the checkpoints under [this folder](./imvoxelnet). 
The file structure should be like:

```
DAIR-V2X/configs/vic3d-spd/late-fusion-image/imvoxelnet/
    ├──trainval_config_i.py
    ├──vic3d_latefusion_imvoxelnet_i.pth
    ├──trainval_config_v.py
    ├──vic3d_latefusion_imvoxelnet_v.pth
```

**b. Run the following commands for evaluation**

```bash
cd ${DAIR-V2X_ROOT}/v2x
bash scripts/eval_camera_late_fusion_spd.sh 0 0 0 100 --no-comp true
```

The parameters are:

- **CUDA_VISIBLE_DEVICES**: GPU IDs
- **DELAY_K**: the number of previous frames for `vic-async-spd` dataset. `vic-async-spd-0` is equivalent to `vic-sync-spd` dataset
- **EXTEND_RANGE_START**: x_{min} of the interested area of vehicle-egocentric surroundings at Vehicle LiDAR 
- **EXTEND_RANGE_END**: x_{max} of the interested area of vehicle-egocentric surroundings at Vehicle LiDAR 
- **TIME_COMPENSATION**: for `late_fusion`, you can remove the time compensation module by an addtional argument **--no-comp**
- **ONLY_DTC**: only eva detection results


If everything is prepared properly, the output results should be:

```
car 3d IoU threshold 0.50, Average Precision = 17.31
car bev IoU threshold 0.50, Average Precision = 22.53

```