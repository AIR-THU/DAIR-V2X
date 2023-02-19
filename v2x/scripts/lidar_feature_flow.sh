FFNet_workdir='/home/yuhaibao/FFNet-VIC3D'
DATA=${FFNet_workdir}'/data/dair-v2x/DAIR-V2X-Examples/cooperative-vehicle-infrastructure'
SPLIT=train
SPLIT_DATA_PATH="../data/split_datas/example-cooperative-split-data.json"
OUTPUT="../cache/vic-feature-flow"
VEHICLE_MODEL_PATH=${FFNet_workdir}'/ffnet_work_dir/work_dir_ffnet/latest.pth'
VEHICLE_CONFIG_NAME=${FFNet_workdir}'/ffnet_work_dir/config_ffnet.py'
CUDA_VISIBLE_DEVICES=$1 \

python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model feature_flow \
  --dataset vic-sync \
  --split $SPLIT \
  --split-data-path $SPLIT_DATA_PATH \
  --veh-config-path $VEHICLE_CONFIG_NAME \
  --veh-model-path $VEHICLE_MODEL_PATH \
  --device $CUDA_VISIBLE_DEVICES \
  --pred-class car \
  --sensortype lidar \
  --extended-range 0 -39.68 -3 100 39.68 1