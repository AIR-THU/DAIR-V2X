DATA="../data/DAIR-V2X/cooperative-vehicle-infrastructure"
OUTPUT="../cache/vic-early-lidar"
rm -r ../cache

MODEL_ROOT='../configs/vic3d/early-fusion-pointcloud/pointpillars'
MODEL_NAME='vic3d_earlyfusion_veh_pointpillars_67fe2b82320754481ef37f176b647e43.pth'
CONFIG_NAME='trainval_config.py'

SPLIT_DATA_PATH="../data/split_datas/cooperative-split-data.json"

# srun --gres=gpu:a100:1 --time=1-0:0:0 --job-name "dair-v2x" \
CUDA_VISIBLE_DEVICES=$1
FUSION_METHOD=$2
DELAY_K=$3
EXTEND_RANGE_START=$4
EXTEND_RANGE_END=$5
python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model $FUSION_METHOD \
  --dataset vic-async \
  --k $DELAY_K \
  --split val \
  --split-data-path $SPLIT_DATA_PATH \
  --veh-config-path $MODEL_ROOT/$CONFIG_NAME \
  --veh-model-path $MODEL_ROOT/$MODEL_NAME \
  --device ${CUDA_VISIBLE_DEVICES} \
  --pred-class car \
  --sensortype lidar \
  --extended-range $EXTEND_RANGE_START -39.68 -3 $EXTEND_RANGE_END 39.68 1 \
  --overwrite-cache