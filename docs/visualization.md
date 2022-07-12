## Visualization tutorial

We provide the tools to visualize the 3d label in images and point clouds, and visualize the prediction results.

#### visualize 3d label in image

##### example:

If you want to visualize the 3d label in images, you can run following commands.

```bash
cd ${dair_v2x_root}
python tools/visualize/vis_label_in_image.py --path ${data_root} --output-file ./vis_results
```

- **path** refers to the directory of the images that want be visualized. It can be ${DAIR-V2X-V_ROOT}, ${DAIR-V2X-I_ROOT}, ${DAIR-V2X-C-I_ROOT}, or ${DAIR-V2X-C-V_ROOT}.
- **save_path** refers to the path of the results of visualization.


#### visualize 3d label in point cloud 
If you want to visualize the 3d label in point cloud, you can run following commands.

```bash
cd ${dair_v2x_root}
python tools/visualize/vis_label_in_3d.py --task pcd_label --pcd-path ${pcd_path} --label-path ${label_json_path}
```
- **--task** refers to the type of task you choose to visualize, the optional values are '**fusion**', '**single**', '**pcd_label**'. 
Here we should set the  **--task** as '**pcd_label**'.
- **--pcd-path** refers to the the path of the pcd file that want be visualized.
- **--label-path** refers to the the label path of the pcd file that want be visualized.

#### visualize 3d label with prediction results

##### example:
After evaluating the TCLF on VIC-Aync-2 dataset with following commands
```bash
cd ${dair_v2x_root}
cd v2x
bash scripts/eval_lidar_late_fusion_pointpillars.sh 0 late_fusion 2 0 100
```
you will generate following cache files including the model prediction results.
The cache file structure should be like
```
└── cache
    ├───── tmps
    └───── vic-late-lidar
       ├───── inf
       ├───── veh
       └───── result
```


If you want to visualize the label and the VIC3D predictionn, you can run following commands.
```bash
cd ${dair_v2x_root}
python tools/visualize/vis_label_in_3d.py --task fusion --path v2x/cache/vic-late-lidar --id 0
```

- **--task** refers to the type of task you choose to visualize, the optional values are '**fusion**', '**single**', '**pcd_label**'.
- **--path** refers to the pickle file generated during inference.
- **--id** refers to the 'filename' you want to visualize.