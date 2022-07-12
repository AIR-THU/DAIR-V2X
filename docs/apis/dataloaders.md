## DAIR-V2X Dataset

We provide four dataset classes, namely `VIC-Sync`, `VIC-Async`, `DAIR-V2X-V` and `DAIR-V2X-I`. The datasets for segmentation task and tracking task will be provided in future work. All the datasets are the subclass of `torch.utils.data`. You can construct them with the following code:
```
dataset = SUPPROTED_DATASETS[dataset](path, split, sensortype, extended_range)
```
- **dataset** refers to the dataset type including `VIC-Sync`, `VIC-Async`, `DAIR-v2x-v` and `DAIR-v2x-i`.

- **path** refers to the directory where DAIR-V2X dataset is stored.

- **split** refers to the dataset split. Available choices are `train`, `val`, `test` and `valtest`.

- **sensortype** refers to the different sensor. `lidar` and `camera` are supported now. 

- **extended_range** is a bounding box denoted as [minx, miny, minz, maxx, maxy, maxz], which represents the intrested area (which is often an extension of the vehicle's range of point cloud) under the vehicle LiDAR coordinate system. Vehicles outside the specific box will be filtered out. 

### Format
We take `VIC-Sync` as an example. Each element of the `VIC-Sync` is a tuple. You can enumerate all data frames in the following way:
```
for VICFrame, label, filt in dataset:
	# Your code here
```
#### VICFrame
You can access to the infrastructure frame class or vehicle frame class by:
```
VICFrame.inf_frame    # The infrastructure frame, member of InfFrame
VICFrame.veh_frame    # The vehicle frame, member of InfFrame
```
We provide `Transform` class carrying out the coordinate transformation you need:
```
trans=VICFrame.transform("from_coord","to_coord")
point_new=trans(point)
```
The following coordinate transformation are supported:
```
Infrastructure_image ->'Infrastructure_camera'->'Infrastructure_lidar'->'world'
                                                                           ^
                                                                           |
                'Vehicle_image'->'Vehicle_camera'->'Vehicle_lidar'->'Vehicle_novatel'

```
You can access the VICFrame values by their keys:
| Key                             | Value                             |
| -------------------------------- | -------------------------------- |
| `infrastructure_image_path`      | path to the infrastructure side image    |
| `infrastructure_pointcloud_path`   | path to the infrastructure side point cloud  |
| `vehicle_image_path`                | path to the vehicle side image |
| `vehicle_pointcloud_path` | path to the vehicle side point cloud    |
| `cooperative_label_path`     | path to the cooperative label |
|`system_error_offset`| the time difference (ms) between the infrastructure frame and vehicle frame |

#### InfFrame

`InfFrame` refers to the infrastructure frame class. We provide APIs which loads the point cloud (`inf_frame.point_cloud(data_format="array"/"file"/"tensor")`) or image (`inf_frame.image(data_format="array"/"file"/"tensor")`) of this frame.

You can also access the frame values by their keys which are listed below:

| Key                             | Value                             |
| -------------------------------- | -------------------------------- |
| `image_path`                       | path to the image            |
| `image_timestamp`                  | the timestamp of the image      |
| `label_camera_path`                | path to the annotation of image |
| `ip`                               | ip of the camera               |
| `camera_id`                        | id of the camera       |
| `pointcloud_path`                  | path to point cloud      |
| `pointcloud_timestamp`             | the timestamp of the point cloud |
| `label_lidar_path`                 | path to the annotation of point cloud |
| `lidar_id`                         | id of the LiDAR   |
| `intersection_loc`                 | name of the intersection       |
| `batch_start_id`                   | start id of the continuous frames |
| `batch_end_id`                     | end id of the continuous frames |
| `calib_virtuallidar_to_world_path`        | path of the calibration file from virtuallidar coordinate system to world coordinate system  |
| `calib_virtuallidar_to_cam_path`          | path of the calibration file from virtuallidar coordinate system to camera coordinate system  |
| `calib_camera_intrisinc_path`      | path of the camera intrinsics file                    |


#### VICFrame.veh_frame

`veh_frame` refers to the vehicle frame class. We provide APIs which loads the point cloud (`inf_frame.point_cloud(data_format="array"/"file"/"tensor")`) or image (`inf_frame.image(data_format="array"/"file"/"tensor")`) of this frame. 
You can also access the frame values by their keys listed below:

| Key                             | Value                             |
| -------------------------------- | -------------------------------- |
| `image_path`                       | path to the image |
| `image_timestamp`                  | the timestamp of the image |
| `label_camera_path`                | path to the annotation of image |
| `pointcloud_path`                  | path to point cloud |
| `pointcloud_timestamp`             | the timestamp of the point cloud  |
| `label_lidar_path`                 | path to the annotation of point cloud |
| `intersection_loc`                 | name of the intersection  |
| `batch_start_id`                   | start id of the continuous frames |
| `batch_end_id`                     | end id of the continuous frames |
| `calib_lidar_to_camera_path`  | path of the calibration file from lidar coordinate system to camera coordinate system |
| `calib_lidar_to_novatel_path` | path of the calibration file from lidar coordinate system to NovAtel coordinate system |
| `calib_novatel_to_world_path` | path of the calibration file from NovAtel coordinate system to world coordinate system |
| `calib_camera_intrisinc_path`      | path of the camera intrinsics file  |

#### Label

`label` refers to the vehicle-infrastructure collaborative annotations, the format of which is as followings.

| Key         | Value                                                        |
| ----------- | ------------------------------------------------------------ |
| `boxes_3d`  | Numpy Float64 Array, [N, 8, 3], representing the 3D bounding box |
| `labels_3d` | Numpy String Array, [N], representing the class of each vehicle (including `car`, `van`,`truck`,`bus`) |
| `scores_3d` | Numpy Float64 Array, which is all 1 in label                 |


#### Filt

`filt` is a filter which decides if the prediction box should be retained since that we are only intrested in boxes within `extended_range`.

### Other functions

#### VIC-Async.prev_inf_frame

Given the pointcloud id of the current vehicle frame, this function queries the previous infrastructure frame captured by the same sensors. If such frame does not exsit, the returned value will be `None`. Here is an example of calling the function:

```
pointcloud_id = inf_frame.id["lidar"]
prev_frame = dataset.prev_inf_frame(pointcloud_id)
prev_pointcloud_id = prev_frame.id["lidar"]
prev_prev_frame = dataset.prev_inf_frame(prev_pointcloud_id)
```

