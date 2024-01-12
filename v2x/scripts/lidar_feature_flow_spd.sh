FFNet_workdir=$2 # '/home/yuhaibao/FFNet-VIC3D'
export PYTHONPATH=$PYTHONPATH:${FFNet_workdir}

DELAY_K=$3
DATA=${FFNet_workdir}'/data/v2x-seq/V2X-Seq-SPD'
VAL_DATA_PATH=${FFNet_workdir}'/data/v2x-seq/flow_data_jsons/flow_data_info_val_'${DELAY_K}'.json'
OUTPUT="../cache/vic-feature-flow-spd"
VEHICLE_MODEL_PATH=${FFNet_workdir}'/ffnet_work_dir/release-checkpoints/ffnet-v2x-spd.pth'
VEHICLE_CONFIG_NAME=${FFNet_workdir}'/configs/ffnet_spd/config_ffnet.py'

CUDA_VISIBLE_DEVICES=$1 

python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model feature_flow \
  --test-mode $4 \
  --dataset vic-sync-spd \
  --val-data-path $VAL_DATA_PATH \
  --veh-config-path $VEHICLE_CONFIG_NAME \
  --veh-model-path $VEHICLE_MODEL_PATH \
  --device $CUDA_VISIBLE_DEVICES \
  --pred-class car \
  --sensortype lidar \
  --extended-range 0 -39.68 -3 100 39.68 1
