## English | [简体中文](./README_zh-CN.md)

## DAIR-V2X
### Data Structure
```
single-infrastructure-side              # DAIR-V2X-I Dataset
    ├── image			      
        ├── {id}.jpg                    
    ├── velodyne                        
        ├── {id}.pcd                 
    ├── calib                          
        ├── camera_intrinsic            
            ├── {id}.json              
        ├── virtuallidar_to_camera     
            ├── {id}.json              
    ├── label                         
        ├── camera                      # Labeled data in Infrastructure Virtual LiDAR Coordinate System fitting objects in image based on image frame time
            ├── {id}.json
        ├── virtuallidar                # Labeled data in Infrastructure Virtual LiDAR Coordinate System fitting objects in point cloud based on point cloud frame time
            ├── {id}.json
    ├── data_info.json                  # Relevant index information of the Infrastructure data
single-vehicle-side                     # DAIR-V2X-V
    ├── image		                
        ├── {id}.jpg
    ├── velodyne                       
        ├── {id}.pcd                    
    ├── calib                         
        ├── camera_intrinsic           
            ├── {id}.json
        ├── lidar_to_camera             
            ├── {id}.json
    ├── label				
        ├── camera                      # Labeled data in Vehicle LiDAR Coordinate System fitting objects in image based on image frame time
            ├── {id}.json
        ├── lidar                       # Labeled data in Vehicle LiDAR Coordinate System fitting objects in point cloud based on point cloud frame time
            ├── {id}.json
    ├── data_info.json                  # Relevant index information of the Vehicle data
cooperative-vehicle-infrastructure      # DAIR-V2X-C
    ├── infrastructure-side             # DAIR-V2X-C-I
        ├── image		        
            ├── {id}.jpg
        ├── velodyne                    
            ├── {id}.pcd               
        ├── calib                     
            ├── camera                
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
---
### Introduction to data-info.json
#### single-infrastructure-side/data_info.json

```json
{
  "image_path",
  "pointcloud_path",
  "label_virtuallidar_path",
  "label_camera_path",
  "calib_virtuallidar_to_camera_path",
  "calib_camera_intrinsic_path"
}
```

#### single-vehicle-side/data_info.json

```json
{
  "image_path",
  "image_timestamp",
  "pointcloud_path",
  "pointcloud_timestamp",
  "label_lidar_path",
  "label_camera_path",
  "calib_lidar_to_camera_path",
  "calib_camera_intrinsic_path"
}
```


#### cooperative-vehicle-infrastructure/infrastructure-side/data_info.json

```json
{
  "image_path",
  "image_timestamp",
  "pointcloud_path",
  "pointcloud_timestamp",
  "label_lidar_path",
  "label_camera_path",
  "calib_virtuallidar_to_world_path",
  "calib_camera_intrinsic_path",
  "batch_id",
  "intersection_loc",
  "batch_start_id",
  "batch_end_id"
}
```

**Comment**：

- Infrastructure and vehicle frame with the same "batch_id" share the same segments.

#### cooperative-vehicle-infrastructure/vehicle-side/data_info.json

```json
{
  "image_path",
  "image_timestamp",
  "pointcloud_path",
  "pointcloud_timestamp",
  "label_lidar_path",
  "label_camera_path",
  "calib_lidar_to_camera_path",
  "calib_lidar_to_novatel_path",
  "calib_novatel_to_world_path",
  "calib_camera_intrinsic_path",
  "batch_id",
  "intersection_loc",
  "batch_start_id",
  "batch_end_id"
}
```


##### cooperative-vehicle-infrastructure/cooperative/data_info.json

```json
{
  "infrastructure_image_path",
  "infrastructure_pointcloud_path",
  "vehicle_image_path",
  "vehicle_pointcloud_path",
  "cooperative_label_path"
}
```


---
### Single-view Annotation File

```json
{
  "type": type,                        
  "truncated_state": truncated_state,  
  "occluded_state": occluded_state,     
  "2d_box": {                          
    "xmin": xmin, 
    "ymin": ymin, 
    "xmax": xmax, 
    "ymax": ymax
  }, 
  "3d_dimensions": {                  
    "h": height, 
    "w": width, 
    "l": length
  }, 
  "3d_location": {               
    "x": x, 
    "y": y, 
    "z": z
  }, 
  "rotation": rotation              
}
```

**Comment**

- 10 object classes, including: Car, Truck, Van, Bus, Pedestrian, Cyclist, Tricyclist,
  Motorcyclist, Barrowlist, and TrafficCone.


---
### Cooperative Annotation File

```json
{
  "type": type,                      
  "world_8_points": 8 corners of 3d bounding box,
  "system_error_offset": {
    "delta_x": delta_x,
    "delta_y": delta_y,
  }
}
```

**Comment**

We only consider the four class ["Car", "Truck", "Van", "Bus"] and generate 9311 annotation files.

---

### Statics

DAIR-V2X is the first large-scale, multi-modality, multi-view dataset for Vehicle-Infrastructure Cooperative Autonomous Driving (VICAD), with 2D&3D object annotations. All data is captured from real scenarios.
- Totally 71254 LiDAR frames and 71254 Camera images:
  - DAIR-V2X Cooperative Dataset (DAIR-V2X-C): 38845 LiDAR frames, 38845 Camera images
  - DAIR-V2X Infrastructure Dataset (DAIR-V2X-I): 10084 LiDAR frames, 10084 Camera images
  - DAIR-V2X Vehicle Dataset (DAIR-V2X-V): 22325 LiDAR frames, 22325 Camera images 
    
We split 50%, 20% and 30% of the dataset into a training set, validation set, and testing set separately. The training set and validation set is now available, and the testing set will be released along with the subsequent challenge activities. 

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

- Institute for AI Industry Research, Tsinghua University (AIR)
- Beijing High-level Autonomous Driving Demonstration Area
- Beijing Connected and Autonomous Vehicles Technology Co., Ltd
- Baidu Apollo
- Beijing Academy of Artificial Intelligence，BAAI

---

### Contaction

Email: dair@air.tsinghua.edu.cn