## [English](./README.md) | 简体中文

## DAIR-V2X车路协同数据集
### 目录结构
```
single-infrastructure-side              # 路端数据集（DAIR-V2X-I）
    ├── image			        # 图像
        ├── {id}.jpg                    
    ├── velodyne                        # 点云（为方便研究，已转到虚拟LiDAR坐标系下）
        ├── {id}.pcd                 
    ├── calib                           # 标定参数
        ├── camera_intrinsic            # 相机参数
            ├── {id}.json              
        ├── virtuallidar_to_camera      # 虚拟LiDAR坐标系到相机坐标系变换参数
            ├── {id}.json              
    ├── label                           # 标注文件
        ├── camera                      # 标注文件（以图像时间戳为基准，3D标注贴合图像中的障碍物）
            ├── {id}.json
        ├── virtuallidar                # 标注文件（以点云时间戳为基准，3D标注贴合点云中的障碍物）
            ├── {id}.json
    ├── data_info.json                  # 数据索引
single-vehicle-side                     # 车端数据集（DAIR-V2X-V）
    ├── image		                # 图像
        ├── {id}.jpg
    ├── velodyne                        # 点云
        ├── {id}.pcd                    
    ├── calib                           # 标定参数
        ├── camera_intrinsic            # 相机参数
            ├── {id}.json
        ├── lidar_to_camera             # LiDAR坐标系到相机坐标系变换参数
            ├── {id}.json
    ├── label				# 标注文件
        ├── camera                      # 标注文件（以图像时间戳为基准，3D标注贴合图像中的障碍物）
            ├── {id}.json
        ├── lidar                       # 标注文件（以点云时间戳为基准，3D标注贴合点云中的障碍物）
            ├── {id}.json
    ├── data_info.json                  # 数据索引
cooperative-vehicle-infrastructure      # 车路协同数据集（DAIR-V2X-C）
    ├── infrastructure-side             # 车路协同路端
        ├── image		        # 图像
            ├── {id}.jpg
        ├── velodyne                    # 点云（为方便研究，已转到虚拟LiDAR坐标系下）
            ├── {id}.pcd               
        ├── calib                       # 标定参数
            ├── camera                  # 相机参数
                ├── {id}.json         
            ├── virtuallidar_to_world   # 虚拟LiDAR坐标系到世界坐标系变换参数（世界坐标系经过简单位置处理）
                ├── {id}.json          
            ├── virtuallidar_to_camera  # 虚拟LiDAR坐标系到相机坐标系变换参数
                ├── {id}.json          
        ├── label			# 标注文件：路端数据标注
            ├── camera                  # 标注文件（以图像时间戳为基准，3D标注贴合图像中的障碍物）
                ├── {id}.json
            ├── virtuallidar            # 标注文件（以点云时间戳为基准，3D标注贴合点云中的障碍物）
                ├── {id}.json
        ├── data_info.json              # 数据索引
    ├── vehicle-side                    # 车路协同车端：此处车端id与路端id非一一对应
        ├── image		        # 图像
            ├── {id}.jpg
        ├── velodyne                    # 点云（LiDAR坐标系下）
            ├── {id}.pcd               
        ├── calib                       # 标定参数和定位
            ├── camera_intrinsic        # 相机参数
                ├── {id}.json
            ├── lidar_to_camera         # LiDAR坐标系到相机坐标系变换参数
                ├── {id}.json
            ├── lidar_to_novatel        # LiDAR坐标系到NovAtel坐标系变换参数
                ├── {id}.json
            ├── novatel_to_world        # NovAtel在世界坐标系下定位坐标（世界坐标系经过简单位置处理）
                ├── {id}.json
        ├── label			# 标注文件：车端数据标注
            ├── camera                  # 标注文件（以图像时间戳为基准，3D标注贴合图像中的障碍物）
                ├── {id}.json
            ├── lidar                   # 标注文件（以点云时间戳为基准，3D标注贴合点云中的障碍物）
                ├── {id}.json
        ├── data_info.json              # 数据索引
    ├── cooperative                     # 融合标注
        ├── label_world                 # 融合标注：利用半自动方式生成车端与路端联合视角下的标注，位于世界坐标系，可利用开源代码转换到车端LiDAR坐标系
            ├── {id}.json               
        ├── data_info.json              # 数据索引
```
---
### 索引文件格式
#### DAIR-V2X-I路端data_info.json组织结构
json文件由一个列表组织而成，列表项的字段和含义如下表所示：

| 字段                             | 含义                             |
| -------------------------------- | --------------------------------- |
| `image_path`                         | 图像路径                        |
| `pointcloud_path`                    | 点云路径                        |
| `label_virtuallidar_path`            | 以点云时间戳为基准标注结果路径      |
 | `label_camera_path`                  | 以图像时间戳为基准标注结果路径      |
| `calib_virtuallidar_to_camera_path`  | 虚拟LiDAR坐标系到相机坐标系参数路径 |
| `calib_camera_intrinsic_path`        | 相机参数路径                     |

#### DAIR-V2X-V车端data_info.json组织结构
json文件由一个列表组织而成，列表项的字段和含义如下表所示：

| 字段                                | 含义                             |
| ---------------------------------- | -------------------------------- |
| `image_path`                       | 图像路径                          |
| `image_timestamp`                  | 图像时间戳                        |
| `pointcloud_path`                  | 点云路径                          |
| `pointcloud_timestamp`             | 点云时间戳                        |
| `label_lidar_path`                 | 以点云时间戳为基准标注结果路径        |
| `label_camera_path`                | 以图像时间戳为基准标注结果路径        |
| `calib_lidar_to_camera_path`       | LiDAR坐标系到相机坐标系参数路径      |
| `calib_camera_intrinsic_path`      | 相机内参路径                      |

#### DAIR-V2X-C路端data_info.json组织结构

json文件由一个列表组织而成，列表项的字段和含义如下表所示：

| 字段                             | 含义                             |
| -------------------------------- | -------------------------------- |
| `image_path`                       | 图像路径                         |
| `image_timestamp`                  | 图像时间戳                       |
| `pointcloud_path`                  | 点云路径                         |
| `pointcloud_timestamp`             | 点云时间戳                       |
| `label_lidar_path`                 | 以点云时间戳为基准标注结果路径 |
| `label_camera_path`                | 以图像时间戳为基准标注结果路径 |
| `calib_virtuallidar_to_world_path`   | 虚拟LiDAR坐标系到世界坐标系参数路径  |
| `calib_virtuallidar_to_camera_path`  | 虚拟LiDAR坐标系到相机坐标系参数路径  |
| `calib_camera_intrinsic_path`      | 相机参数路径                     |
| `batch_id`                         | 数据片段编号：车端与路端共享相同的batch_id |
| `intersection_loc`                 | 数据采集所在路口名称                     |
| `batch_start_id`                   | 数据片段起始编号                       |
| `batch_end_id`                     | 数据片段结束编号             |

**备注**：

- 路端图像、点云编号从[ `batch_start_id`, `batch_end_id` ]为一段，表示同一个路口下采集得到的数据帧，按时间顺序排列

#### DAIR-V2X-C车端data_info.json组织结构

json文件由一个列表组织而成，列表项的字段和含义如下表所示：

| 字段                             | 含义                             |
| -------------------------------- | -------------------------------- |
| `image_path`                       | 图像路径                         |
| `image_timestamp`                  | 图像时间戳                       |
| `pointcloud_path`                  | 点云路径                         |
| `pointcloud_timestamp`             | 点云时间戳                       |
| `label_lidar_path`                 | 以点云时间戳为基准标注结果路径 |
| `label_camera_path`                | 以图像时间戳为基准标注结果路径 |
| `calib_lidar_to_camera_path`  | LiDAR坐标系到相机坐标系参数路径 |
| `calib_lidar_to_novatel_path` | LiDAR坐标系到NovAtel坐标系参数路径 |
| `calib_novatel_to_world_path` | NovAtel坐标系到世界坐标系参数路径 |
| `calib_camera_intrinsic_path`      | 相机参数路径                     |
| `batch_id`                         | 数据片段编号：车端与路端共享相同的batch_id |
| `intersection_loc`                 | 数据采集所在路口名称                     |
| `batch_start_id`                   | 数据片段起始编号                       |
| `batch_end_id`                     | 数据片段结束编号             |


##### 车路协同融合标注data_info.json

json文件由一个列表组织而成，列表项的字段和含义如下表所示：

| 字段                             | 含义                             |
| -------------------------------- | -------------------------------- |
| `infrastructure_image_path`                  | 路端图像路径       |
| `infrastructure_pointcloud_path`             | 路端点云路径       |
| `vehicle_image_path`                | 车端图像路径                     |
| `vehicle_pointcloud_path`                  | 车端点云路径              |
| `cooperative_label_path`             | 融合标注路径：利用路端和车端对应帧label+半自动生成                 |

---
### 单侧标注格式

标注文件由一个列表组织而成，一个列表项对应一个目标的标签，列表项的格式如下所示：

```json
{
  "type": type,                         // 障碍物类型
  "truncated_state": truncated_state,   // 障碍物截断情况：从[0, 1, 2]中取值，分别表示不截断、横向截断、纵向截断 
  "occluded_state": occluded_state,     // 障碍物遮挡情况：从[0, 1, 2]中取值，分别表示不遮挡、0%～50%遮挡，50%～100%遮挡
  "alpha": alpha,                       // 观察者视角，从[-pi, pi]中取值
  "2d_box": {                           // 图像中2D bounding box框
    "xmin": xmin, 
    "ymin": ymin, 
    "xmax": xmax, 
    "ymax": ymax
  }, 
  "3d_dimensions": {                    // 3D bounding box长宽高
    "h": height, 
    "w": width, 
    "l": length
  }, 
  "3d_location": {                      // 3D bounding box中心点坐标
    "x": x, 
    "y": y, 
    "z": z
  }, 
  "rotation": rotation              // 3D bounding box绕中心点z轴正方向为旋转轴，从y轴正方向开始旋转的角度
}
```

**备注**

标签共有10类，如下所示。

| 类型              | 标签名称          |
| ----------------- | ----------------- |
| 小汽车            | Car               |
| 卡车/大货车       | Trunk             |
| 面包车/厢式货车   | Van               |
| 公交车/大型旅客车 | Bus               |
| 行人              | Pedestrian        |
| 自行车            | Cyclist           |
| 三轮车            | Tricyclist        |
| 摩托车            | Motorcyclist      |
| 手推车            | Barrowlist        |
| 交通锥筒          | TrafficCone       |

---
### 融合标注格式

标注文件由一个列表组织而成，一个列表项对应一个目标的标签，列表项的格式如下所示：

```json
{
  "type": type,                         // 障碍物类型
  "world_8_points": 8 corners of 3d bounding box,  // 障碍物3d标注信息，位于世界坐标系；需要转到车端LiDAR坐标系下得到长、宽、高、3d location、朝向等信息；当前标注文件中其他3D信息不可用
  "system_error_offset": { // 路端与车端相对标定存在的系统误差，人工二次修正；未融合标注的为""
    "delta_x": delta_x,
    "delta_y": delta_y,
  }
}
```

**备注**

目前融合标注只考虑如下4类，生成约1w帧。

| 类型              | 标签名称          |
| ----------------- | ----------------- |
| 小汽车            | Car               |
| 卡车/大货车       | Trunk             |
| 面包车/厢式货车   | Van               |
| 公交车/大型旅客车 | Bus               |

---

### 统计信息

- 总计71254帧图像数据和71254帧点云数据；本次只释放train/val部分，test部分将随后续challenge释放
  - DAIR-V2X车路协同数据集(DAIR-V2X-C)，包含38845帧图像数据和38845帧点云数据
    - 车端包含18330帧图像数据和18330帧点云数据
    - 路端包含20515帧图像数据和20515帧点云数据
  - DAIR-V2X路端数据集(DAIR-V2X-I)，包含10084帧图像数据和10084帧点云数据
  - DAIR-V2X车端数据集(DAIR-V2X-V)，包含22325帧图像数据和22325帧点云数据

---

### Citation

```
@inproceedings{yu2022dairv2x,
    title={DAIR-V2X: A Large-Scale Dataset for Vehicle-Infrastructure Cooperative 3D Object Detection},
    author={Yu, Haibao and Luo, Yizhen and Shu, Mao and Huo, Yiyi and Yang, Zebang and Shi, Yifeng and Guo, Zhenglong and Li, Hanyu and Hu, Xing and Yuan, Jirui and Nie, Zaiqing},
    booktitle={IEEE/CVF Conf.~on Computer Vision and Pattern Recognition (CVPR)},
    month = jun,
    year={2022}
}
```

---

### Organizations

清华大学智能产业研究院（AIR）

北京市高级别自动驾驶示范区

北京车网科技发展有限公司

百度Apollo

北京智源人工智能研究院

---

### Contaction

Email: dair@air.tsinghua.edu.cn