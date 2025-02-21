<div align="center">   
  
# DAIR-V2X and OpenDAIRV2X: Towards General and Real-World Cooperative Autonomous Driving

</div>

<h3 align="center">
    <a href="https://thudair.baai.ac.cn/index">Project Page</a> |
    <a href="#dataset">Dataset Download</a> |
    <a href="https://arxiv.org/abs/2204.05575">arXiv</a> |
    <a href="https://github.com/AIR-THU/DAIR-V2X/">OpenDAIRV2X</a> 
</h3>

<br><br>
![teaser](resources/deployment-visual.png)

## Table of Contents:
1. [Highlights](#high)
2. [News](#news)
3. [Dataset Download](#dataset)
4. [Getting Started](#start)
5. [Major Features](#features)
6. [Benchmark](#benchmark)
7. [Citation](#citation)
8. [Contaction](#contaction)

## Highlights <a name="high"></a>
- DAIR-V2X: The first real-world dataset for research on vehicle-to-everything autonomous driving. It comprises a total of 71,254 frames of image data and 71,254 frames of point cloud data.
- V2X-Seq:  The first large-scale, real-world, and sequential V2X dataset, which includes data frames, trajectories, vector maps, and traffic lights captured from natural scenery.  V2X-Seq comprises two parts: V2X-Seq-SPD (Sequential Perception Dataset), which includes more than 15,000 frames captured from 95 scenarios; V2X-Seq-TFD (Trajectory Forecasting Dataset), which contains about 80,000 infrastructure-view scenarios, 80,000 vehicle-view scenarios, and 50,000 cooperative-view scenarios captured from 28 intersections' areas, covering 672 hours of data.
- OpenDAIR-V2X: An open-sourced framework for supporting the research on  vehicle-to-everything autonomous driving.

## News <a name="news"></a>
* [2025.01] 🔥 We will hold 2nd MEIS Workshop at CVPR2025. More information will be [MEIS Workshop](https://coop-intelligence.github.io/). We will call for paper and hold three challenges.
* [2025.01] 🔥 We have released v1.0 code for UniV2X at [here](https://github.com/AIR-THU/UniV2X).
* [2024.12] Our [UniV2X](https://arxiv.org/abs/2404.00717) has been accepted by AAAI2025. UniV2X is the first end-to-end framework that unifies all vital modules as well as diverse driving views into a network for cooperative autonomous driving.
* [2024.10] We held 1st cooperative intelligence workshop at ECCV2024. More information is [MAAS Workshop](https://coop-intelligence.github.io/eccv2024/).
* [2024.09] Our [V2X-Gaph](https://github.com/AIR-THU/V2X-Graph) has been accepted by NeurIPs2024! V2X-Graph. V2X-Graph is the first interpretable and end-to-end learning framework for cooperative motion forecasting.
* [2024.07] Our CTCE[https://arxiv.org/abs/2408.10531] has been accpeted by ITSC2024! CTCE is a novel sequential framework for cooperative perception. 
* [2024.03] Our new Dataset RCooper, a real-world large-scale dataset for roadside cooperative perception, has been accepted by CVPR2024! Please follow [RCooper](https://github.com/AIR-THU/DAIR-RCooper) for the latest news.
* [2024.01] Our [QUEST](https://arxiv.org/abs/2308.01804) has been been accpeted by ICRA2024.
* [2023.10] We have released the code for [V2X-Seq-SPD](https://github.com/AIR-THU/DAIR-V2X) and [V2X-Seq-TFD](https://github.com/AIR-THU/DAIR-V2X-Seq).
* [2023.09] Our [FFNET](https://github.com/haibao-yu/FFNet-VIC3D) has been accpeted by Neurips2023.
* [2023.05] V2X-Seq dataset is availale [here](https://thudair.baai.ac.cn/index).
* [2023.03] Our new dataset "V2X-Seq: A Large-Scale Sequential Dataset for Vehicle-Infrastructure Cooperative Perception and Forecasting" has been accepted by CVPR2023. Congratulations! We will release the dataset sooner. Please follow [DAIR-V2X-Seq](https://github.com/AIR-THU/DAIR-V2X-Seq) for the latest news.
* [2023.03] We have released training code for our [FFNET](https://github.com/haibao-yu/FFNet-VIC3D), and our OpenDAIRV2X now supports evaluating [FFNET](https://github.com/haibao-yu/FFNet-VIC3D).
* [2022.11] We have held the first [VIC3D Object Detection challenge](https://aistudio.baidu.com/aistudio/competition/detail/522/0/introduction). 
* [2022.07] We have released the OpenDAIRV2X codebase v1.0.0.
  The current version can faciliate the researchers to use the DAIR-V2X dataset and reproduce the benchmarks.
* [2022.03] Our Paper "DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure Cooperative 3D Object Detection" has been accepted by CVPR2022.
  Arxiv version could be seen [here](https://arxiv.org/abs/2204.05575).
* [2022.02] DAIR-V2X dataset is availale [here](https://thudair.baai.ac.cn/index).

## Dataset Download <a name="dataset"></a>
 - DAIR-V2X-C-Example: [google_drive_link](https://drive.google.com/file/d/1y8bGwI63TEBkDEh2JU_gdV7uidthSnoe/view?usp=drive_link)
 - V2X-Seq-SPD-Example: [google_drive_link](https://drive.google.com/file/d/1gjOmGEBMcipvDzu2zOrO9ex_OscUZMYY/view?usp=drive_link)
 - V2X-Seq-TFD-Example: [google_drive_link](https://drive.google.com/file/d/1-Ri92z6rkH14vAOFOx5xhfzvFxBptgAA/view?usp=sharing)

 Note: We have also provided the full dataset (DAIR-V2X and V2X-Seq) at [Public-V2X-Datasets](https://drive.google.com/drive/folders/1gnrw5llXAIxuB9sEKKCm6xTaJ5HQAw2e?usp=sharing).

## Getting Started <a name="start"></a>
Please refer to [getting_started.md](docs/get_started.md) for the usage and benchmarks reproduction of DAIR-V2X dataset.

Please refer to [get_started_spd.md](docs/get_started_spd.md) for the usage and benchmarks reproduction of V2X-Seq-SPD dataset.

## Benchmark <a name="benchmark"></a>

You can find more benchmark in [SV3D-Veh](configs/sv3d-veh), [SV3D-Inf](configs/sv3d-inf), [VIC3D](configs/vic3d) and [VIC3D-SPD](configs/vic3d-spd/). 

Part of the VIC3D detection benchmarks based on DAIR-V2X-C dataset:

| Modality  | Fusion  | Model      | Dataset   | AP-3D (IoU=0.5)  |        |        |         | AP-BEV (IoU=0.5)  |       |        |         |   AB   |
| :-------: | :-----: | :--------: | :-------: | :----: | :----: | :----: | :-----: | :-----: | :---: | :----: | :-----: | :----: |
|           |         |            |           | Overall | 0-30m | 30-50m | 50-100m | Overall | 0-30m | 30-50m | 50-100m |        |
| Image     | VehOnly | ImvoxelNet | VIC-Sync  |    9.13   | 19.06         | 5.23  | 0.41   | 10.96   | 21.93           | 7.28  | 0.78   | 0     |
|       | Late-Fusion | ImvoxelNet | VIC-Sync  |   18.77   | 33.47         | 9.43  | 8.62    | 24.85   | 39.49           | 14.68  | 14.96   | 309.38|                    
|Pointcloud | VehOnly | PointPillars | VIC-Sync | 48.06  | 47.62 | 63.51  | 44.37   | 52.24   | 30.55 | 66.03  |  48.36  | 0      |     
|  | Early Fusion | PointPillars | VIC-Sync    | 62.61                    | 64.82                  | 68.68                   | 56.57                    | 68.91                     | 68.92                   | 73.64                    | 65.66                     | 1382275.75 |
|       | Late-Fusion | PointPillars | VIC-Sync | 56.06  | 55.69 | 68.44  | 53.60   | 62.06   | 61.52 | 72.53  | 60.57   | 478.61 |                                                     
|       | Late-Fusion | PointPillars |VIC-Async-2| 52.43 | 51.13 | 67.09  | 49.86   | 58.10   | 57.23 | 70.86  | 55.78   | 478.01 |
|       | TCLF        | PointPillars |VIC-Async-2| 53.37 | 52.41 | 67.33  | 50.87   | 59.17   | 58.25 | 71.20  | 57.43   | 897.91 |

Part of the VIC3D detection and tracking benchmarks based on V2X-Seq-SPD:

| Modality | Fusion      | Model       | Dataset      | AP 3D (Iou=0.5) | AP BEV (Iou=0.5) | MOTA   | MOTP   | AMOTA  | AMOTP  | IDs | AB(Byte) |                                                                                        
|----------|-------------|-------------|--------------|-----------------|------------------|--------|--------|--------|--------|-----|----------|
| Image    | Veh Only    | ImvoxelNet  | VIC-Sync-SPD | 8.55            | 10.32            | 10.19 | 57.83 | 1.36 | 14.75 | 4   |          |
| Image    | Late Fusion | ImvoxelNet  | VIC-Sync-SPD | 17.31           | 22.53            | 21.81 | 56.67 | 6.22 | 25.24 | 47  | 3300     |


## TODO List <a name="TODO List"></a>
- [x] Dataset Release
- [x] Dataset API
- [x] Evaluation Code
- [x] All detection benchmarks based on DAIR-V2X dataset
- [x] Benchmarks for detection and tracking tasks with different fusion strategies for Image based on V2X-Seq-SPD dataset
- [ ] All benchmarks for detection and tracking tasks based on V2X-Seq-SPD dataset


## Citation <a name="citation"></a>
Please consider citing our paper if the project helps your research with the following BibTex:
```bibtex
@inproceedings{v2x-seq,
  title={V2X-Seq: A large-scale sequential dataset for vehicle-infrastructure cooperative perception and forecasting},
  author={Yu, Haibao and Yang, Wenxian and Ruan, Hongzhi and Yang, Zhenwei and Tang, Yingjuan and Gao, Xu and Hao, Xin and Shi, Yifeng and Pan, Yifeng and Sun, Ning and Song, Juan and Yuan, Jirui and Luo, Ping and Nie, Zaiqing},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2023},
}
```
```bibtex
@inproceedings{dair-v2x,
  title={Dair-v2x: A large-scale dataset for vehicle-infrastructure cooperative 3d object detection},
  author={Yu, Haibao and Luo, Yizhen and Shu, Mao and Huo, Yiyi and Yang, Zebang and Shi, Yifeng and Guo, Zhenglong and Li, Hanyu and Hu, Xing and Yuan, Jirui and Nie, Zaiqing},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={21361--21370},
  year={2022}
}
```

## Contaction <a name="contaction"></a>

If any questions and suggenstations, please email to dair@air.tsinghua.edu.cn. 

## Related Resources

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

- [DAIR-V2X-Seq](https://github.com/AIR-THU/DAIR-V2X-Seq) (:rocket:Ours!)
- [FFNET](https://github.com/haibao-yu/FFNet-VIC3D) (:rocket:Ours!)
- [mmdet3d](https://github.com/open-mmlab/mmdetection3d)
- [pypcd](https://github.com/dimatura/pypcd)
- [AB3DMOT](https://github.com/xinshuoweng/AB3DMOT)

