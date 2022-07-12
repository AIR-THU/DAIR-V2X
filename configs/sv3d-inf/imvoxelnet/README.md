# ImVoxelNet: Image to Voxels Projection for Monocular and Multi-View General-Purpose 3D Object Detection

> [ImVoxelNet: Image to Voxels Projection for Monocular and Multi-View General-Purpose 3D Object Detection](https://arxiv.org/abs/2106.01178)

## Introduction

We implement ImVoxelNet and provide the results and checkpoints on DAIR-V2X-I datasets with MMDetection3D.

## Results and models

| Modality | Model | Car  |        |      | Pedestrain |        |      | Cyclist |        |      | Download |
| :------: | :---: | :--: | :----: | :--: | :--------: | :----: | :--: | :-----: | :----: | :--: | :------: |
|          |       | Easy | Middle | Hard |    Easy    | Middle | Hard |  Easy   | Middle | Hard |          |
| Image | ImVoxelNet | 44.78 | 37.58  | 37.55 | 6.81  | 6.746  | 6.73 | 21.06   | 13.57  | 13.17 |  [model](https://drive.google.com/file/d/1hmeyJzHAIIBamM8rQFSqCuLba2ZehwmU/view?usp=sharing)

## Training & Evaluation

### Data Preparation

#### Download data and organise as follows

```
# For DAIR-V2X-I Dataset located at ${DAIR-V2X-I_DATASET_ROOT}
└─── single-infrastructure-side
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
ln -s ${DAIR-V2X-I_DATASET_ROOT}/single-infrastructure-side ./data/DAIR-V2X
```

#### Create Kitti-format data (Option for model training)

Data creation should be under the gpu environment.
```commandline
# Kitti Format
cd ${dair-v2x_root}/dair-v2x
python tools/dataset_converter/dair2kitti.py --source-root ./data/DAIR-V2X/single-infrastructure-side \
    --target-root ./data/DAIR-V2X/single-infrastructure-side \
    --split-path ./data/split_datas/single-infrastructure-split-data.json \
    --label-type camera --sensor-view infrastructure
```

In the end, the data and info files should be organized as follows

```
└─── single-infrastructure-side                
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
    Before training the detectors, we should follow MMDetection3D to convert the "./data/DAIR-V2X/single-infrastructure-side" into specific training format.
    We train the ImVoxelNet for 12 epochs.
    We evaluate the models on the valid part of DAIR-V2X-I. 
    We set [0.5, 0.25, 0.25] as the IoU threshold for [Car, Pedestrain, Cyclist]. 
    Please refer [trainval_config.py](./trainval_config.py) for more evaluation details.
    We provide the evaluation results with 3D Average Precision.

## Citation

```latex
@inproceedings{rukhovich2022imvoxelnet,
  title={Imvoxelnet: Image to voxels projection for monocular and multi-view general-purpose 3d object detection},
  author={Rukhovich, Danila and Vorontsova, Anna and Konushin, Anton},
  booktitle={Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision},
  pages={2397--2406},
  year={2022}
}
```