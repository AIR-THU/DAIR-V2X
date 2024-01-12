## SPD Dataset

We provide four spd dataset classes, namely `VICSyncDatasetSPD`, `VICAsyncDatasetSPD`, `DAIRV2XVSPD` and `DAIRV2XISPD`.
All the datasets are the subclass of `torch.utils.data.dataset.Dataset`.
You can construct them with the following code:
```
dataset = SUPPROTED_DATASETS[dataset](path, split, sensortype, extended_range)
```
- **dataset** refers to the dataset type including `vic-sync-spd`, `vic-async-spd`, `dair-v2x-v-spd` and `dair-v2x-i-spd`.

- **path** refers to the directory where SPD dataset is stored.

- **split** refers to the dataset split. Available choices are `train`, `val`, `test` and `valtest`.

- **sensortype** refers to the different sensor. `lidar` and `camera` are supported now. 

- **extended_range** is a bounding box denoted as [minx, miny, minz, maxx, maxy, maxz], which represents the intrested area (which is often an extension of the vehicle's range of point cloud) under the vehicle LiDAR coordinate system. Vehicles outside the specific box will be filtered out. 

### Format
We take `vic-sync-spd` as an example. Each element of the `vic-sync-spd` is a tuple. You can enumerate all data frames in the following way:
```
for VICFrameSPD, label, filt in dataset:
	# Your code here
```
#### VICFrameSPD
You can access to the infrastructure frame class or vehicle frame class by:
```
VICFrameSPD.inf_frame    # The infrastructure frame, member of InfFrameSPD
VICFrameSPD.veh_frame    # The vehicle frame, member of VehFrameSPD
```
We provide `Transform` class carrying out the coordinate transformation you need:
```
trans=VICFrameSPD.transform("from_coord","to_coord")
point_new=trans(point)
```
The following coordinate transformation are supported:
```
Infrastructure_image ->'Infrastructure_camera'->'Infrastructure_lidar'->'world'
                                                                           ^
                                                                           |
                'Vehicle_image'->'Vehicle_camera'->'Vehicle_lidar'->'Vehicle_novatel'

```
note: In SPD, when converting from the Infrastructure_lidar to Vehicle_lidar, the usage of delta_x and delta_y in the system_error_offset is different from that in VIC3D.

You can access the VICFrameSPD values by their keys:

| Key                       | Value                                                                       |
|---------------------------|-----------------------------------------------------------------------------|
| `infrastructure_frame`    | infrastructure frame datainfo                                               |
| `vehicle_frame`           | vehicle frame datainfo                                                      |

#### InfFrameSPD

`InfFrameSPD` refers to the infrastructure frame class. We provide APIs which loads the point cloud (`inf_frame.point_cloud(data_format="array"/"file"/"tensor")`) or image (`inf_frame.image(data_format="array"/"file"/"tensor")`) of this frame.

You can also access the frame values by their keys which are listed below:

| Key                                 | Value                                                                                        |
|-------------------------------------|----------------------------------------------------------------------------------------------|
| `image_path`                        | path to the image                                                                            |
| `image_timestamp`                   | the timestamp of the image                                                                   |
| `pointcloud_path`                   | path to point cloud                                                                          |
| `pointcloud_timestamp`              | the timestamp of the point cloud                                                             |
| `label_lidar_std_path`              | path to the annotation of point cloud                                                        |
| `label_camera_std_path`             | path to the annotation of image                                                              |
| `calib_virtuallidar_to_world_path`  | path of the calibration file from virtuallidar coordinate system to world coordinate system  |
| `calib_virtuallidar_to_camera_path` | path of the calibration file from virtuallidar coordinate system to camera coordinate system |
| `calib_camera_intrisinc_path`       | path of the camera intrinsics file                                                           |
| `frame_id`                          | id of the current frame                                                                      |
| `sequence_id`                       | id of the current sequence                                                                   |
| `num_frames`                        | number of the continuous frames                                                              |
| `start_frame_id`                    | start id of the continuous frames                                                            |
| `end_frame_id`                      | end id of the continuous frames                                                              |
| `intersection_loc`                  | name of the intersection                                                                     |
| `camera_ip`                         | ip of the camera                                                                             |
| `camera_id`                         | id of the camera                                                                             |
| `lidar_id`                          | id of the LiDAR                                                                              |


#### VehFrameSPD

`VehFrameSPD` refers to the vehicle frame class. We provide APIs which loads the point cloud (`veh_frame.point_cloud(data_format="array"/"file"/"tensor")`) or image (`veh_frame.image(data_format="array"/"file"/"tensor")`) of this frame. 
You can also access the frame values by their keys listed below:

| Key                           | Value                                                                                  |
|-------------------------------|----------------------------------------------------------------------------------------|
| `image_path`                  | path to the image                                                                      |
| `image_timestamp`             | the timestamp of the image                                                             |
| `pointcloud_path`             | path to point cloud                                                                    |
| `pointcloud_timestamp`        | the timestamp of the point cloud                                                       |
| `label_lidar_std_path`        | path to the annotation of point cloud                                                  |
| `label_camera_std_path`       | path to the annotation of image                                                        |
| `calib_lidar_to_camera_path`  | path of the calibration file from lidar coordinate system to camera coordinate system  |
| `calib_lidar_to_novatel_path` | path of the calibration file from lidar coordinate system to NovAtel coordinate system |
| `calib_novatel_to_world_path` | path of the calibration file from NovAtel coordinate system to world coordinate system |
| `calib_camera_intrisinc_path` | path of the camera intrinsics file                                                     |
| `frame_id`                    | id of the current frame                                                                |
| `sequence_id`                 | id of the current sequence                                                             |
| `num_frames`                  | number of the continuous frames                                                        |
| `start_frame_id`              | start id of the continuous frames                                                      |
| `end_frame_id`                | end id of the continuous frames                                                        |
| `intersection_loc`            | name of the intersection                                                               |

#### Label

`label` refers to the vehicle-infrastructure collaborative annotations, based on Vehicle LiDAR coordinate system. The format of which is as followings.

| Key         | Value                                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------------|
| `boxes_3d`  | Numpy Float64 Array, [N, 8, 3], representing the 3D bounding box                                       |
| `labels_3d` | Numpy String Array, [N], representing the class of each vehicle (including `car`, `van`,`truck`,`bus`) |
| `scores_3d` | Numpy Float64 Array, which is all 1 in label                                                           |


#### Filt

`filt` is a filter which decides if the prediction box should be retained since that we are only intrested in boxes within `extended_range`.


