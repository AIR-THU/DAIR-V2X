## Data converter tutorial
We provide the tools to process the DAIR-V2X dataset, such as convert the dataset into Kitti format.

### DAIR2Kitti

`tools/dataset_converter/dair2kitti.py` can convert the DAIR-V2X dataset into Kitti format.
    
       python tools/dataset_converter/dair2kitti.py [--source-root ${SOURCE_ROOT}] [--target-root ${TARGET_ROOT}] [--split-path ${SPLIT_PATH}] [--label-type ${LABEL_TYPE}] [--sensor-view ${SENSOR_VIEW}] [--no-classmerge ${NO_CLASSMERGE}] 
    
### Pointcloud Transformation

`tools/dataset_converter/point_cloud_i2v.py` can convert the point cloud from infrastructure LiDAR coordinate system to ego-vehicle LiDAR coordinate system.

### Label Convertion

`tools/dataset_converter/label_world2v.py` can convert the 3D labels which are represented with 8 points and located in world coordinate system into the 3D label which are represented with `[x, y, z, w, h, l, theta]` and located in ego-vehicle LiDAR coordinate system.

### Calibration Convertion

`tools/dataset_converter/calib_i2v.py` can get the calibration parameters from infrastructure LiDAR coordinate system to ego-vehicle LiDAR coordinate system. 