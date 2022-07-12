# PointPillars: Fast Encoders for Object Detection from Point Clouds
> [PointPillars: Fast Encoders for Object Detection from Point Clouds](https://arxiv.org/abs/1812.05784)

## Introduction
We implement PointPillars and provide the results and checkpoints on DAIR-V2X-V datasets with MMDetection3D.

## Results and models
|  Modality  |     Model    |  Car  |        |       | Pedestrain |        |       | Cyclist |        |       | Download |
|:----------:|:------------:|:-----:|:------:|:-----:|:----------:|:------:|:-----:|:-------:|:------:|:-----:|:--------:|
|            |              |  Easy | Middle |  Hard |    Easy    | Middle |  Hard |   Easy  | Middle |  Hard |          |
| Pointcloud | PointPillars | 61.76 | 49.02  | 43.45 | 33.40      | 24.68  | 22.39 | 38.24   | 33.80  | 32.35 |  [model](https://drive.google.com/file/d/1T5Aw5ComvaJg1HBSS4QENdiGUWbX41m4/view?usp=sharing) |

## Training & Evaluation

### Data Preparation
#### Download data and organise as follows

```
# For DAIR-V2X-V Dataset located at ${DAIR-V2X-V_DATASET_ROOT}
└─── single-vehicle-side
     ├───── image
     ├───── velodyne
     ├───── calib
     ├───── label
     └───── data_info.json        
```

#### Create a symlink to the dataset root

```
cd ${dair-v2x_root}/dair-v2x
mkdir ./data/DAIR-V2X
ln -s ${DAIR-V2X-V_DATASET_ROOT}/single-vehicle-side ./data/DAIR-V2X
```

#### Create Kitti-format data (Option for model training)

Data creation should be under the gpu environment.
```commandline
# Kitti Format
cd ${dair-v2x_root}/dair-v2x
python tools/dataset_converter/dair2kitti.py --source-root ./data/DAIR-V2X/single-vehicle-side \
    --target-root ./data/DAIR-V2X/single-vehicle-side \
    --split-path ./data/split_datas/single-vehicle-split-data.json \
    --label-type lidar --sensor-view vehicle
```

In the end, the data and info files should be organized as follows
```
└─── single-vehicle-side             
     ├───── image
     ├───── velodyne
     ├───── calib
     ├───── label
     ├───── data_info.json
     ├───── ImageSets
     └───── training
        ├───── image_2
        ├───── velodyne
        ├───── label_2
        └───── calib
```

### Training & Evaluation

* Implementation Framework. We directly implement the benchmark with [mmdetection3d-0.17.1](https://github.com/open-mmlab/mmdetection3d/tree/v0.17.1).
* Training & Evaluation details. 
  Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/single-vehicle-side" into specific training format.
  We train the MVX-Net for 40 epochs.
  We evaluate the models on the valid part of DAIR-V2X-V. 
  We set [0.5, 0.25, 0.25] as the IoU threshold for [Car, Pedestrain, Cyclist]. 
  Please refer [trainval_config.py](./trainval_config.py) for more evaluation details.
  We provide the evaluation results with 3D Average Precision.

## Citation

```latex
@inproceedings{lang2019pointpillars,
  title={Pointpillars: Fast encoders for object detection from point clouds},
  author={Lang, Alex H and Vora, Sourabh and Caesar, Holger and Zhou, Lubing and Yang, Jiong and Beijbom, Oscar},
  booktitle={Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition},
  pages={12697--12705},
  year={2019}
}
```