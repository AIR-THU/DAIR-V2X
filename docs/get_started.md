## Get Started with DAIR-V2X

### Installation

Required extertal packages are listed as follows:

```
mmdetection3d==0.17.1, pypcd
```

Firstly follow the instructions [here](https://github.com/open-mmlab/mmdetection3d/blob/master/docs/en/getting_started.md) to install mmdetection3d. Make sure the version of mmdetection3d is exactly 0.17.1.

Note that pypcd pip installing is not compatible with Python3. Therefore [a modified version](https://github.com/dimatura/pypcd) should be manually installed as followings.
```
git clone https://github.com/klintan/pypcd.git
cd pypcd
python setup.py install
```

### An Example of Evaluation

Here we provide an example to evaluate the TCLF on VIC-Async-2 dataset.

#### Data Preparation

##### Download data and organize as follows

Download DAIR-V2X-C dataset [here](https://thudair.baai.ac.cn/cooptest) and organize as follows:

```

# For DAIR-V2X-C Dataset located at ${DAIR-V2X-C_DATASET_ROOT}
├── cooperative-vehicle-infrastructure      # DAIR-V2X-C
    ├── infrastructure-side             # DAIR-V2X-C-I
        ├── image		    
            ├── {id}.jpg
        ├── velodyne                
            ├── {id}.pcd           
        ├── calib                 
            ├── camera_intrinsic            
                ├── {id}.json     
            ├── virtuallidar_to_world   
                ├── {id}.json      
            ├── virtuallidar_to_camera  
                ├── {id}.json      
        ├── label	
            ├── camera                  # Labeled data in Infrastructure Virtual LiDAR Coordinate System fitting objects in image based on image frame time
                ├── {id}.json
            ├── virtuallidar            # Labeled data in Infrastructure Virtual LiDAR Coordinate System fitting objects in point cloud based on point cloud frame time
                ├── {id}.json
        ├── data_info.json              # Relevant index information of Infrastructure data
    ├── vehicle-side                    # DAIR-V2X-C-V
        ├── image		    
            ├── {id}.jpg
        ├── velodyne             
            ├── {id}.pcd           
        ├── calib                 
            ├── camera_intrinsic   
                ├── {id}.json
            ├── lidar_to_camera   
                ├── {id}.json
            ├── lidar_to_novatel  
                ├── {id}.json
            ├── novatel_to_world   
                ├── {id}.json
        ├── label	
            ├── camera                  # Labeled data in Vehicle LiDAR Coordinate System fitting objects in image based on image frame time
                ├── {id}.json
            ├── lidar                   # Labeled data in Vehicle LiDAR Coordinate System fitting objects in point cloud based on point cloud frame time
                ├── {id}.json
        ├── data_info.json              # Relevant index information of the Vehicle data
    ├── cooperative                     # Coopetative Files
        ├── label_world                 # Vehicle-Infrastructure Cooperative (VIC) Annotation files
            ├── {id}.json           
        ├── data_info.json              # Relevant index information combined the Infrastructure data and the Vehicle data
```

##### Create a symlink to the dataset root
```
cd ${dair-v2x_root}/dair-v2x
mkdir ./data/DAIR-V2X
ln -s ${DAIR-V2X-C_DATASET_ROOT}/cooperative-vehicle-infrastructure ${dair-v2x_root}/dair-v2x/data/DAIR-V2X
```

#### Checkpoint Preparation
Download checkpoints trained with mmdetection3d from Google drive: [inf-model](https://drive.google.com/file/d/1BO5dbqmLjC3gTjvQTyfEjhIikFz2P_Om/view?usp=sharing) & [veh-model](https://drive.google.com/file/d/1tY1sqQGGSaRoA8KDeIQPjcUZ20I82wTK/view?usp=sharing). 
Put the checkpoints under [this folder](../configs/vic3d/late-fusion-pointcloud). 
The file structure should be like:

```
configs/vic3d/late-fusion-pointcloud/pointpillars
    ├──trainval_config_i.py
    ├──vic3d_latefusion_inf_pointpillars_596784ad6127866fcfb286301757c949.pth
    ├──trainval_config_v.py
    ├──vic3d_latefusion_veh_pointpillars_a70fa05506bf3075583454f58b28177f.pth
```

#### Evaluation
Run the following commands for evaluation:

```bash
cd ${dair_v2x_root}
cd v2x
bash scripts/eval_lidar_late_fusion_pointpillars.sh 0 late_fusion 2 0 100
```

Or:

```bash
rm -r ./cache
cd v2x

DATA="../data/DAIR-V2X/cooperative-vehicle-infrastructure"
OUTPUT="../cache/vic-late-lidar"
rm -r $OUTPUT
rm -r ../cache
mkdir -p $OUTPUT/result
mkdir -p $OUTPUT/inf/lidar
mkdir -p $OUTPUT/veh/lidar

python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model late_fusion \
  --dataset vic-async \
  --k 2 \
  --split val \
  --split-data-path ../data/split_datas/cooperative-split-data.json \
  --inf-config-path ../configs/vic3d/late-fusion-pointcloud/pointpillars/trainval_config_i.py \
  --inf-model-path ../configs/vic3d/late-fusion-pointcloud/pointpillars/vic3d_latefusion_inf_pointpillars_596784ad6127866fcfb286301757c949.pth \
  --veh-config-path ../configs/vic3d/late-fusion-pointcloud/pointpillars/trainval_config_v.py \
  --veh-model-path ../configs/vic3d/late-fusion-pointcloud/pointpillars/vic3d_latefusion_veh_pointpillars_a70fa05506bf3075583454f58b28177f.pth \
  --device 0 \
  --pred-class car \
  --sensortype lidar \
  --extended-range 0 -39.68 -3 100 39.68 1
```

The key arguments are:

- **input**: the directory where you download our dair-v2x dataset.
- **output**: the directory where your prediction files are placed.
- **model**: the type of your model. Choices are `veh_only`,`inf_only`,`late_fusion`,`early_fusion`. 
- **dataset**: the name of the dataset. Choices are `dair-v2x-v`, `dair-v2x-i`,`vic-sync` and `vic-async`. 
- **k**: the number of previous frames for `vic-async` dataset. `vic-async-0` is equivalent to `vic-sync` dataset.
- **split**: dataset split. Choices are `train`, `val`, `test`, `valtest`. 
- **pred_class**: the prediction class you want to evaluate on.
- **sensortype**: the modality of input data. Choices are `lidar`, `camera` and `multimodality`.
- **extended-range**: the interested area of vehicle-egocentric surroundings, which is described as $[x_{min}, y_{min},z_{min},x_{max},y_{max},z_{max}]$ at Vehicle LiDAR Coordinate.
- **--no-comp**: for `late_fusion`, you can remove the time compensation module by an addtional argument **--no-comp**


### Reproducing Benchmark Results

We release our checkpoints with different modalities and fusion strategies. Refer to the following table for implementation details and downloading the checkpoints.


|  Modality  |    Fusion    |    Model    |   Dataset   |                             Reproduce&Checkpoint                             |
| :----------: | :------------: | :------------: | :-----------: | :-----------------------------------------------------------------------------: |
|   Image   |   VehOnly   |  ImvoxelNet  |  VIC-Sync  |       [README](../configs/vic3d/late-fusion-image/imvoxelnet/README.md)       |
|            |   InfOnly   |  ImvoxelNet  |  VIC-Sync  |     [README](../configs/vic3d/late-fusion-image/imvoxelnet/README.md)     |
|            | Late-Fusion |  ImvoxelNet  |  VIC-Sync  |     [README](../configs/vic3d/late-fusion-image/imvoxelnet/README.md)     |
| Pointcloud |   VehOnly   | PointPillars |  VIC-Sync  | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            |   InfOnly   | PointPillars |  VIC-Sync  | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            | Late-Fusion | PointPillars |  VIC-Sync  | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            | Early-Fusion | PointPillars |  VIC-Sync  | [README](../configs/vic3d/early-fusion-pointcloud/pointpillars/README.md) |
|            | Late-Fusion | PointPillars | VIC-Async-1 | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            | Late-Fusion | PointPillars | VIC-Async-2 | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            | Early-Fusion | PointPillars | VIC-Async-1 | [README](../configs/vic3d/early-fusion-pointcloud/pointpillars/README.md) |
|            |     TCLF     | PointPillars | VIC-Async-1 | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |
|            |     TCLF     | PointPillars | VIC-Async-2 | [README](../configs/vic3d/late-fusion-pointcloud/pointpillars/README.md) |

### API usage

To simply load our DAIR-V2X dataset, please refer to [this](./apis/dataloaders.md).

To visualize LiDAR or camera frames in DAIR-V2X, please refer to [this](./visualization.md).

To evaluate your own VIC3D object detection model with our framework, please refer to [this](./apis/customized_models.md).

To further learn and use our fusion modules, please refer to [this](./apis/fusion_modules.md).