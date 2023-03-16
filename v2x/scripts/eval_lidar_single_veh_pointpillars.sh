DATA="../data/DAIR-V2X/cooperative-vehicle-infrastructure"
OUTPUT="../cache/sv3d-single-lidar"
rm -r ../cache
mkdir -p $OUTPUT/result
mkdir -p $OUTPUT/inf/lidar
mkdir -p $OUTPUT/veh/lidar

MODEL_ROOT='../configs/sv3d-veh/pointpillars'
MODEL_NAME='sv3d_veh_pointpillars_0ad9e1bd3bb211316d4dd0ce19c7d009.pth'
CONFIG_NAME='trainval_config.py'

SPLIT_DATA_PATH="../data/split_datas/cooperative-split-data.json"

# srun --gres=gpu:a100:1 --time=1-0:0:0 --job-name "dair-v2x" \
CUDA_VISIBLE_DEVICES=$1
SINGLE_METHOD=$2
EXTEND_RANGE_START=$3
EXTEND_RANGE_END=$4
python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model $SINGLE_METHOD \
  --dataset vic-sync-v2 \
  --split val \
  --split-data-path $SPLIT_DATA_PATH \
  --veh-config-path $MODEL_ROOT/$CONFIG_NAME \
  --veh-model-path $MODEL_ROOT/$MODEL_NAME \
  --device ${CUDA_VISIBLE_DEVICES} \
  --pred-class car \
  --sensortype lidar \
  --extended-range $EXTEND_RANGE_START -39.68 -3 $EXTEND_RANGE_END 39.68 1 \
  --overwrite-cache