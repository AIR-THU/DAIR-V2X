FFNet_workdir='/home/yuhaibao/FFNet-VIC3D'
DATA=${FFNet_workdir}'/data/dair-v2x/DAIR-V2X/cooperative-vehicle-infrastructure'
SPLIT=val
SPLIT_DATA_PATH="../data/split_datas/cooperative-split-data.json"
OUTPUT="../cache/vic-feature-fusion-baseline"
VEHICLE_MODEL_PATH=${FFNet_workdir}'/ffnet_work_dir/work_dir_baseline-V1/ffnet_without_prediction.pth'
VEHICLE_CONFIG_NAME=${FFNet_workdir}'/ffnet_work_dir/config_basemodel.py'
CUDA_VISIBLE_DEVICES=$1 \

python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model feature_fusion \
  --dataset vic-sync \
  --split $SPLIT \
  --split-data-path $SPLIT_DATA_PATH \
  --veh-config-path $VEHICLE_CONFIG_NAME \
  --veh-model-path $VEHICLE_MODEL_PATH \
  --device $CUDA_VISIBLE_DEVICES \
  --pred-class car \
  --sensortype lidar \
  --extended-range 0 -39.68 -3 100 39.68 1 