dataset_type = "KittiDataset"
data_root = "../../../data/DAIR-V2X/single-infrastructure-side/"
class_names = ["Pedestrian", "Cyclist", "Car"]
point_cloud_range = [0, -40, -3, 70.4, 40, 1]
voxel_size = [0.05, 0.05, 0.1]
input_modality = dict(use_lidar=True, use_camera=False)

model = dict(
    type="VoxelNet",
    voxel_layer=dict(
        max_num_points=5, point_cloud_range=point_cloud_range, voxel_size=voxel_size, max_voxels=(16000, 40000)
    ),
    voxel_encoder=dict(type="HardSimpleVFE"),
    middle_encoder=dict(
        type="SparseEncoder", in_channels=4, sparse_shape=[41, 1600, 1408], order=("conv", "norm", "act")
    ),
    backbone=dict(type="SECOND", in_channels=256, layer_nums=[5, 5], layer_strides=[1, 2], out_channels=[128, 256]),
    neck=dict(type="SECONDFPN", in_channels=[128, 256], upsample_strides=[1, 2], out_channels=[256, 256]),
    bbox_head=dict(
        type="Anchor3DHead",
        num_classes=3,
        in_channels=512,
        feat_channels=512,
        use_direction_classifier=True,
        anchor_generator=dict(
            type="Anchor3DRangeGenerator",
            ranges=[
                [0, -40.0, -0.6, 70.4, 40.0, -0.6],
                [0, -40.0, -0.6, 70.4, 40.0, -0.6],
                [0, -40.0, -1.78, 70.4, 40.0, -1.78],
            ],
            sizes=[[0.6, 0.8, 1.73], [0.6, 1.76, 1.73], [1.6, 3.9, 1.56]],
            rotations=[0, 1.57],
            reshape_out=False,
        ),
        diff_rad_by_sin=True,
        bbox_coder=dict(type="DeltaXYZWLHRBBoxCoder"),
        loss_cls=dict(type="FocalLoss", use_sigmoid=True, gamma=2.0, alpha=0.25, loss_weight=1.0),
        loss_bbox=dict(type="SmoothL1Loss", beta=0.1111111111111111, loss_weight=2.0),
        loss_dir=dict(type="CrossEntropyLoss", use_sigmoid=False, loss_weight=0.2),
    ),
    train_cfg=dict(
        assigner=[
            dict(
                type="MaxIoUAssigner",
                iou_calculator=dict(type="BboxOverlapsNearest3D"),
                pos_iou_thr=0.35,
                neg_iou_thr=0.2,
                min_pos_iou=0.2,
                ignore_iof_thr=-1,
            ),
            dict(
                type="MaxIoUAssigner",
                iou_calculator=dict(type="BboxOverlapsNearest3D"),
                pos_iou_thr=0.35,
                neg_iou_thr=0.2,
                min_pos_iou=0.2,
                ignore_iof_thr=-1,
            ),
            dict(
                type="MaxIoUAssigner",
                iou_calculator=dict(type="BboxOverlapsNearest3D"),
                pos_iou_thr=0.6,
                neg_iou_thr=0.45,
                min_pos_iou=0.45,
                ignore_iof_thr=-1,
            ),
        ],
        allowed_border=0,
        pos_weight=-1,
        debug=False,
    ),
    test_cfg=dict(
        use_rotate_nms=True,
        nms_across_levels=False,
        nms_thr=0.01,
        score_thr=0.1,
        min_bbox_size=0,
        nms_pre=100,
        max_num=50,
    ),
)

db_sampler = dict(
    data_root=data_root,
    info_path=data_root + "/kitti_dbinfos_train.pkl",
    rate=1.0,
    prepare=dict(filter_by_difficulty=[-1], filter_by_min_points=dict(Car=5, Pedestrian=10, Cyclist=10)),
    classes=class_names,
    sample_groups=dict(Car=12, Pedestrian=6, Cyclist=6),
)
file_client_args = dict(backend="disk")
train_pipeline = [
    dict(type="LoadPointsFromFile", coord_type="LIDAR", load_dim=4, use_dim=4, file_client_args=dict(backend="disk")),
    dict(type="LoadAnnotations3D", with_bbox_3d=True, with_label_3d=True, file_client_args=dict(backend="disk")),
    dict(
        type="ObjectSample",
        db_sampler=dict(
            data_root=data_root,
            info_path=data_root + "/kitti_dbinfos_train.pkl",
            rate=1.0,
            prepare=dict(filter_by_difficulty=[-1], filter_by_min_points=dict(Car=5, Pedestrian=10, Cyclist=10)),
            classes=class_names,
            sample_groups=dict(Car=12, Pedestrian=6, Cyclist=6),
        ),
    ),
    dict(
        type="ObjectNoise",
        num_try=100,
        translation_std=[1.0, 1.0, 0.5],
        global_rot_range=[0.0, 0.0],
        rot_range=[-0.78539816, 0.78539816],
    ),
    dict(type="RandomFlip3D", flip_ratio_bev_horizontal=0.5),
    dict(type="GlobalRotScaleTrans", rot_range=[-0.78539816, 0.78539816], scale_ratio_range=[0.95, 1.05]),
    dict(type="PointsRangeFilter", point_cloud_range=point_cloud_range),
    dict(type="ObjectRangeFilter", point_cloud_range=point_cloud_range),
    dict(type="PointShuffle"),
    dict(type="DefaultFormatBundle3D", class_names=class_names),
    dict(type="Collect3D", keys=["points", "gt_bboxes_3d", "gt_labels_3d"]),
]
test_pipeline = [
    dict(type="LoadPointsFromFile", coord_type="LIDAR", load_dim=4, use_dim=4, file_client_args=dict(backend="disk")),
    dict(
        type="MultiScaleFlipAug3D",
        img_scale=(1333, 800),
        pts_scale_ratio=1,
        flip=False,
        transforms=[
            dict(type="GlobalRotScaleTrans", rot_range=[0, 0], scale_ratio_range=[1.0, 1.0], translation_std=[0, 0, 0]),
            dict(type="RandomFlip3D"),
            dict(type="PointsRangeFilter", point_cloud_range=point_cloud_range),
            dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
            dict(type="Collect3D", keys=["points"]),
        ],
    ),
]
eval_pipeline = [
    dict(type="LoadPointsFromFile", coord_type="LIDAR", load_dim=4, use_dim=4, file_client_args=dict(backend="disk")),
    dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
    dict(type="Collect3D", keys=["points"]),
]
data = dict(
    samples_per_gpu=6,
    workers_per_gpu=4,
    train=dict(
        type="RepeatDataset",
        times=2,
        dataset=dict(
            type="KittiDataset",
            data_root=data_root,
            ann_file=data_root + "/kitti_infos_train.pkl",
            split="training",
            pts_prefix="velodyne_reduced",
            pipeline=[
                dict(
                    type="LoadPointsFromFile",
                    coord_type="LIDAR",
                    load_dim=4,
                    use_dim=4,
                    file_client_args=dict(backend="disk"),
                ),
                dict(
                    type="LoadAnnotations3D",
                    with_bbox_3d=True,
                    with_label_3d=True,
                    file_client_args=dict(backend="disk"),
                ),
                dict(
                    type="ObjectSample",
                    db_sampler=dict(
                        data_root=data_root,
                        info_path=data_root + "/kitti_dbinfos_train.pkl",
                        rate=1.0,
                        prepare=dict(
                            filter_by_difficulty=[-1], filter_by_min_points=dict(Car=5, Pedestrian=10, Cyclist=10)
                        ),
                        classes=class_names,
                        sample_groups=dict(Car=12, Pedestrian=6, Cyclist=6),
                    ),
                ),
                dict(
                    type="ObjectNoise",
                    num_try=100,
                    translation_std=[1.0, 1.0, 0.5],
                    global_rot_range=[0.0, 0.0],
                    rot_range=[-0.78539816, 0.78539816],
                ),
                dict(type="RandomFlip3D", flip_ratio_bev_horizontal=0.5),
                dict(type="GlobalRotScaleTrans", rot_range=[-0.78539816, 0.78539816], scale_ratio_range=[0.95, 1.05]),
                dict(type="PointsRangeFilter", point_cloud_range=point_cloud_range),
                dict(type="ObjectRangeFilter", point_cloud_range=point_cloud_range),
                dict(type="PointShuffle"),
                dict(type="DefaultFormatBundle3D", class_names=class_names),
                dict(type="Collect3D", keys=["points", "gt_bboxes_3d", "gt_labels_3d"]),
            ],
            modality=dict(use_lidar=True, use_camera=False),
            classes=class_names,
            test_mode=False,
            box_type_3d="LiDAR",
        ),
    ),
    val=dict(
        type="KittiDataset",
        data_root=data_root,
        ann_file=data_root + "/kitti_infos_val.pkl",
        split="training",
        pts_prefix="velodyne_reduced",
        pipeline=[
            dict(
                type="LoadPointsFromFile",
                coord_type="LIDAR",
                load_dim=4,
                use_dim=4,
                file_client_args=dict(backend="disk"),
            ),
            dict(
                type="MultiScaleFlipAug3D",
                img_scale=(1333, 800),
                pts_scale_ratio=1,
                flip=False,
                transforms=[
                    dict(
                        type="GlobalRotScaleTrans",
                        rot_range=[0, 0],
                        scale_ratio_range=[1.0, 1.0],
                        translation_std=[0, 0, 0],
                    ),
                    dict(type="RandomFlip3D"),
                    dict(type="PointsRangeFilter", point_cloud_range=point_cloud_range),
                    dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
                    dict(type="Collect3D", keys=["points"]),
                ],
            ),
        ],
        modality=dict(use_lidar=True, use_camera=False),
        classes=class_names,
        test_mode=True,
        box_type_3d="LiDAR",
    ),
    test=dict(
        type="KittiDataset",
        data_root=data_root,
        ann_file=data_root + "/kitti_infos_val.pkl",
        split="training",
        pts_prefix="velodyne_reduced",
        pipeline=[
            dict(
                type="LoadPointsFromFile",
                coord_type="LIDAR",
                load_dim=4,
                use_dim=4,
                file_client_args=dict(backend="disk"),
            ),
            dict(
                type="MultiScaleFlipAug3D",
                img_scale=(1333, 800),
                pts_scale_ratio=1,
                flip=False,
                transforms=[
                    dict(
                        type="GlobalRotScaleTrans",
                        rot_range=[0, 0],
                        scale_ratio_range=[1.0, 1.0],
                        translation_std=[0, 0, 0],
                    ),
                    dict(type="RandomFlip3D"),
                    dict(type="PointsRangeFilter", point_cloud_range=point_cloud_range),
                    dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
                    dict(type="Collect3D", keys=["points"]),
                ],
            ),
        ],
        modality=dict(use_lidar=True, use_camera=False),
        classes=class_names,
        test_mode=True,
        box_type_3d="LiDAR",
    ),
)
evaluation = dict(
    interval=1,
    pipeline=[
        dict(
            type="LoadPointsFromFile", coord_type="LIDAR", load_dim=4, use_dim=4, file_client_args=dict(backend="disk")
        ),
        dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
        dict(type="Collect3D", keys=["points"]),
    ],
)
lr = 0.0018
optimizer = dict(type="AdamW", lr=0.0018, betas=(0.95, 0.99), weight_decay=0.01)
optimizer_config = dict(grad_clip=dict(max_norm=10, norm_type=2))
lr_config = dict(policy="cyclic", target_ratio=(10, 0.0001), cyclic_times=1, step_ratio_up=0.4)
momentum_config = dict(policy="cyclic", target_ratio=(0.8947368421052632, 1), cyclic_times=1, step_ratio_up=0.4)
runner = dict(type="EpochBasedRunner", max_epochs=40)
checkpoint_config = dict(interval=1)
log_config = dict(interval=50, hooks=[dict(type="TextLoggerHook"), dict(type="TensorboardLoggerHook")])
dist_params = dict(backend="nccl")
log_level = "INFO"
work_dir = "./work_dirs/hv_second_secfpn_6x8_80e_kitti-3d-3class"
load_from = None
resume_from = None
workflow = [("train", 1)]
gpu_ids = range(0, 1)
