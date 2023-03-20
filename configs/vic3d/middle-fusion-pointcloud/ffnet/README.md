# FFNet: Feature Flow Net

##  Introduction

We provide the evaluation of Feature Flow Net (FFNet) for solving VIC3D object detection. Please refer [FFNet-VIC3D](https://github.com/haibao-yu/FFNet-VIC3D) for  more information about training and configuation.

## Evaluation  Results and Models

| Modality   | Model   | Latency (ms)     | Overall(AP 3D Iou = 0.5) | Overall(AP BEV Iou = 0.5) | AB(Byte)           |
| ---------- | ------ | ------------ | ----------- | ------------------------ | ------------------------- |
| Pointcloud | FFNET  | 0    | 55.81                    | 63.54                     | 1.2×10<sup>5</sup> |
| Pointcloud | FFNET  | 100    | 55.48                    | 63.14                     | 1.2×10<sup>5</sup> |
| Pointcloud | FFNET  | 200    | 55.37                    | 63.20                     | 1.2×10<sup>5</sup> |

## Evaluation Processs

### Data Preparation

We evaluate the models on DAIR-V2X dataset. For downloading DAIR-V2X dataset, please refer to the guidelines in [DAIR-V2X](https://thudair.baai.ac.cn/cooptest). After downloading the dataset, we should preprcocess the dataset as the guidelines in [data_preprocess](https://github.com/haibao-yu/FFNet-VIC3D/blob/main/data/dair-v2x/README.md). Here we suggest you take data preparation operation under [FFNET-VIC3D](https://github.com/haibao-yu/FFNet-VIC3D).

### Evaluation
Download [FFNet](https://github.com/haibao-yu/FFNet-VIC3D), configure the environment as described in its README.

 Download [Trainded FFNET Checkpoint](https://drive.google.com/file/d/1eX2wZ7vSxq8y9lAyjHyrmBQ30qNHcFC6/view?usp=sharing) and put this checkpoint under '${Your_FFNet_workdir}/ffnet_work_dir/work_dir_ffnet'.

Then use the following commands to get the evaluation results.

    # An example to get the FFNET evaluation results within [0, 100]m range under 100ms latency, namely VIC-Async-1.
    # bash scripts/lidar_feature_flow.sh [YOUR_CUDA_DEVICE] [YOUR_FFNET_WORKDIR] [DELAY_K] [TEST_MODE]
    cd ${dair-v2x_root}/dair-v2x/v2x
    bash scripts/lidar_feature_flow.sh 0 /home/yuhaibao/FFNet-VIC3D 1 'FlowPred'

* DELAY_K candidates: [0, 1, 2, 3, 4, 5]. 0 denotes VIC-Sync dataset, 1 denotes VIC-Async-1 dataset.
* TEST_MODE candidates: ['FlowPred', 'OriginFeat', 'Async'].  'FlowPred' mode denotes FFNet with feature prdiction; 'Async' mode denotes FFNet without feature prediction, namely feature fusion model; 'OriginFeat' mode denotes that there is no latency.

## Citation

```latex
@inproceedings{yu2023ffnet,
  title={Vehicle-Infrastructure Cooperative 3D Object Detection via Feature Flow Prediction},
  author={Yu, Haibao and Tang, Yingjuan and Xie, Enze and Mao, Jilei and Yuan, Jirui and Luo, Ping and Nie, Zaiqing },
  booktitle={Under Review},
  year={2023}
}
```