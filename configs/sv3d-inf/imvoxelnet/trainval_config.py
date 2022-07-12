dataset_type = "KittiMultiViewDataset"
data_root = "../../../data/DAIR-V2X/single-infrastructure-side/"
class_names = ["Pedestrian", "Cyclist", "Car"]
input_modality = dict(use_lidar=False, use_camera=True)
img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

voxel_size = [0.64, 0.64, 0.32]
point_cloud_range = [0, -39.68, -3, 69.12, 39.68, 0.84]
ped_center = -1.48
cyc_center = -1.48
car_center = -2.66
n_voxels = [int((point_cloud_range[i + 3] - point_cloud_range[i]) / voxel_size[i]) for i in range(3)]
anchor_range_ped = [
    point_cloud_range[0],
    point_cloud_range[1],
    ped_center,
    point_cloud_range[3] - voxel_size[0],
    point_cloud_range[4] - voxel_size[1],
    ped_center,
]
anchor_range_cyc = [
    point_cloud_range[0],
    point_cloud_range[1],
    cyc_center,
    point_cloud_range[3] - voxel_size[0],
    point_cloud_range[4] - voxel_size[1],
    cyc_center,
]
anchor_range_car = [
    point_cloud_range[0],
    point_cloud_range[1],
    car_center,
    point_cloud_range[3] - voxel_size[0],
    point_cloud_range[4] - voxel_size[1],
    car_center,
]

model = dict(
    type="ImVoxelNet",
    pretrained="torchvision://resnet50",
    backbone=dict(
        type="ResNet",
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type="BN", requires_grad=False),
        norm_eval=True,
        style="pytorch",
    ),
    neck=dict(type="FPN", in_channels=[256, 512, 1024, 2048], out_channels=64, num_outs=4),
    neck_3d=dict(type="KittiImVoxelNeck", in_channels=64, out_channels=256),
    bbox_head=dict(
        type="Anchor3DHead",
        num_classes=3,
        in_channels=256,
        feat_channels=256,
        use_direction_classifier=True,
        anchor_generator=dict(
            type="Anchor3DRangeGenerator",
            ranges=[anchor_range_ped, anchor_range_cyc, anchor_range_car],
            sizes=[[0.6, 0.8, 1.73], [0.6, 1.76, 1.73], [1.6, 3.9, 1.56]],
            rotations=[0, 1.57],
            reshape_out=False,
        ),
        diff_rad_by_sin=True,
        bbox_coder=dict(type="DeltaXYZWLHRBBoxCoder"),
        loss_cls=dict(type="FocalLoss", use_sigmoid=True, gamma=2.0, alpha=0.25, loss_weight=1.0),
        loss_bbox=dict(type="SmoothL1Loss", beta=1.0 / 9.0, loss_weight=2.0),
        loss_dir=dict(type="CrossEntropyLoss", use_sigmoid=False, loss_weight=0.2),
    ),
    # n_voxels=(216, 248, 12),
    # voxel_size=(.64, .64, .64)
    n_voxels=n_voxels,
    voxel_size=voxel_size,
)
train_cfg = dict(
    assigner=[
        dict(  # for Pedestrian
            type="MaxIoUAssigner",
            iou_calculator=dict(type="BboxOverlapsNearest3D"),
            pos_iou_thr=0.5,
            neg_iou_thr=0.35,
            min_pos_iou=0.35,
            ignore_iof_thr=-1,
        ),
        dict(  # for Cyclist
            type="MaxIoUAssigner",
            iou_calculator=dict(type="BboxOverlapsNearest3D"),
            pos_iou_thr=0.5,
            neg_iou_thr=0.35,
            min_pos_iou=0.35,
            ignore_iof_thr=-1,
        ),
        dict(  # for Car
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
)
test_cfg = dict(
    use_rotate_nms=True, nms_across_levels=False, nms_thr=0.01, score_thr=0.2, min_bbox_size=0, nms_pre=100, max_num=50
)

train_pipeline = [
    dict(type="LoadAnnotations3D"),
    dict(
        type="MultiViewPipeline",
        n_images=1,
        transforms=[
            dict(type="LoadImageFromFile"),
            # dict(type='RandomFlip', flip_ratio=0.5),
            dict(type="Resize", img_scale=[(1173, 352), (1387, 416)], keep_ratio=True, multiscale_mode="range"),
            dict(type="Normalize", **img_norm_cfg),
            dict(type="Pad", size_divisor=32),
        ],
    ),
    # dict(type='KittiRandomFlip'),
    dict(type="ObjectRangeFilter", point_cloud_range=point_cloud_range),
    dict(type="KittiSetOrigin", point_cloud_range=point_cloud_range),
    dict(type="DefaultFormatBundle3D", class_names=class_names),
    dict(type="Collect3D", keys=["img", "gt_bboxes_3d", "gt_labels_3d"]),
]
test_pipeline = [
    dict(
        type="MultiViewPipeline",
        n_images=1,
        transforms=[
            dict(type="LoadImageFromFile"),
            dict(type="Resize", img_scale=(1280, 384), keep_ratio=True),
            dict(type="Normalize", **img_norm_cfg),
            dict(type="Pad", size_divisor=32),
        ],
    ),
    dict(type="KittiSetOrigin", point_cloud_range=point_cloud_range),
    dict(type="DefaultFormatBundle3D", class_names=class_names, with_label=False),
    dict(type="Collect3D", keys=["img"]),
]

data = dict(
    samples_per_gpu=4,
    workers_per_gpu=3,
    train=dict(
        type="RepeatDataset",
        times=3,
        dataset=dict(
            type=dataset_type,
            data_root=data_root,
            ann_file=data_root + "kitti_infos_train.pkl",
            split="training",
            pts_prefix="velodyne_reduced",
            pipeline=train_pipeline,
            modality=input_modality,
            classes=class_names,
            pcd_limit_range=point_cloud_range,
            test_mode=False,
        ),
    ),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + "kitti_infos_val.pkl",
        split="training",
        pts_prefix="velodyne_reduced",
        pipeline=test_pipeline,
        modality=input_modality,
        classes=class_names,
        pcd_limit_range=point_cloud_range,
        test_mode=True,
    ),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        ann_file=data_root + "kitti_infos_val.pkl",
        split="training",
        pts_prefix="velodyne_reduced",
        pipeline=test_pipeline,
        modality=input_modality,
        classes=class_names,
        pcd_limit_range=point_cloud_range,
        test_mode=True,
    ),
)

optimizer = dict(
    type="AdamW",
    lr=0.0001,
    weight_decay=0.0001,
    paramwise_cfg=dict(custom_keys={"backbone": dict(lr_mult=0.1, decay_mult=1.0)}),
)
optimizer_config = dict(grad_clip=dict(max_norm=35.0, norm_type=2))
lr_config = dict(policy="step", step=[8, 11])
total_epochs = 12

checkpoint_config = dict(interval=1, max_keep_ckpts=1)
log_config = dict(interval=50, hooks=[dict(type="TextLoggerHook"), dict(type="TensorboardLoggerHook")])
evaluation = dict(interval=1)
dist_params = dict(backend="nccl")
find_unused_parameters = True  # todo: fix number of FPN outputs
log_level = "INFO"
load_from = "checkpoint/20210503_214214.pth"
resume_from = None
workflow = [("train", 1)]
