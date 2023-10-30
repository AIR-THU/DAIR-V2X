## Get Started with V2X-Seq-SPD

### Installation

a. Required extertal packages are listed as follows:

```
mmdetection3d==0.17.1, pypcd
```

Firstly follow the instructions [here](https://github.com/open-mmlab/mmdetection3d/blob/master/docs/en/getting_started.md) to install mmdetection3d. Make sure the version of mmdetection3d is exactly 0.17.1.

Note that pypcd pip installing is not compatible with Python3. Therefore, [a modified version](https://github.com/dimatura/pypcd) should be manually installed as followings.
```bash
git clone https://github.com/klintan/pypcd.git
cd pypcd
python setup.py install
```

b. Download AB3DMOT
```
git clone https://github.com/xinshuoweng/AB3DMOT.git

```
Install AB3DMOT refer to [AB3DMOT Installation](https://github.com/xinshuoweng/AB3DMOT/blob/master/docs/INSTALL.md)

Note: Please add the path of AB3DMOT and Xinshuo_PyToolbox to your PYTHONPATH, according to the AB3DMOT Installation.


c. Download DAIR-V2X
```
git clone https://github.com/AIR-THU/DAIR-V2X.git

```

### Data Preparation

#### a.Download data and organize as follows

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

#### b.Create a symlink to the dataset root

```
cd DAIR-V2X
cd ./data/
ln -s ${SPD_DATASET_ROOT}/V2X-Seq-SPD
```
#### c.Convert V2X-Seq-SPD cooperative label to V2X-Seq-SPD-KITTI format (Option for tracking evaluation)
```
cd DAIR-V2X
python tools/dataset_converter/spd2kitti_tracking/coop_label_dair2kitti.py \
   --source-root ./data/V2X-Seq-SPD \
   --target-root ./data/V2X-Seq-SPD-KITTI/cooperative \
   --split-path ./data/split_datas/cooperative-split-data-spd.json \
   --no-classmerge

```
At the end of the process, the data and info files should be organized as follows:

```
DAIR-V2X/data/V2X-Seq-SPD-KITTI/     
    └──── cooperative              
       ├──── training
          ├──── {sequence_id}    
             ├──── label_02
                ├───── {sequence_id}.txt
       ├──── validation
       └──── testing   
```

### Evaluation Example

Here we provide an example to evaluate the late fusion results for VIC3D Tracking on the V2X-Seq-SPD dataset for Image.
We use ImvoxelNet to perceive 2D objects from the infrastructure and ego-vehicle sequential images. Next, we transmit the infrastructure objects to the ego vehicle and fuse them with the ego-vehicle objects based on Euclidean distance measurements. Then we use AB3DMOT to track the fused objects.

#### Detection Checkpoint Preparation
Download checkpoints of ImvoxelNet trained on SPD datasets with mmdetection3d from Google drive: [inf-model](https://drive.google.com/file/d/1XntybUfSXQMZgiZnT7INRYPLBuHXT-Lv/view?usp=sharing) & [veh-model](https://drive.google.com/file/d/1eZWsG3VzMuC8swYfVveM3Zg3fcGR6IvN/view?usp=sharing). 

Put the checkpoints under [this folder](../configs/vic3d-spd/late-fusion-image/imvoxelnet/). 
The file structure should be like:

```
DAIR-V2X/configs/vic3d-spd/late-fusion-image/imvoxelnet/
    ├──trainval_config_i.py
    ├──vic3d_latefusion_imvoxelnet_i.pth
    ├──trainval_config_v.py
    ├──vic3d_latefusion_imvoxelnet_v.pth
```

#### Evaluation

Run the following commands for evaluation:

```bash
cd DAIR-V2X
cd v2x
bash scripts/eval_camera_late_fusion_spd.sh 0 0 0 100 --no-comp
```

The parameters are:

- **CUDA_VISIBLE_DEVICES**: GPU IDs
- **DELAY_K**: the number of previous frames for `vic-async-spd` dataset. `vic-async-spd-0` is equivalent to `vic-sync-spd` dataset.
- **EXTEND_RANGE_START**: x_{min} of the interested area of vehicle-egocentric surroundings at Vehicle LiDAR 
- **EXTEND_RANGE_END**: x_{max} of the interested area of vehicle-egocentric surroundings at Vehicle LiDAR 
- **TIME_COMPENSATION**: for `late_fusion`, you can remove the time compensation module by an addtional argument **--no-comp**


If everything is prepared properly, the output results should be:

```
car 3d IoU threshold 0.50, Average Precision = 17.31
car bev IoU threshold 0.50, Average Precision = 22.53
AMOTA = 0.0622
AMOTP = 0.2524

```

#### Reproducing Benchmark Results
We release our benchmarks for detection and tracking tasks with different fusion strategies for Image. Refer to the [README](../configs/vic3d-spd/late-fusion-image/README.md) for implementation details.

We will soon release the benchmarks for detection and tracking tasks with all modalities, fusion types, and fusion methods for our V2X-Seq-SPD dataset. Please stay tuned!


### API usage

To simply load our V2X-Seq-SPD dataset, please refer to [this](./apis/dataloaders_spd.md).

To visualize LiDAR or camera frames in V2X-Seq-SPD, please refer to [this](./visualization_spd.md).
