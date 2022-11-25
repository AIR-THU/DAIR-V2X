DATA="../data/DAIR-V2X/cooperative-vehicle-infrastructure"
OUTPUT="../cache/vic-late-camera"
rm -r $OUTPUT
rm -r ../cache
mkdir -p $OUTPUT/result
mkdir -p $OUTPUT/inf/camera
mkdir -p $OUTPUT/veh/camera

INFRA_MODEL_PATH="../configs/vic3d/late-fusion-image/imvoxelnet"
INFRA_CONFIG_NAME="trainval_config_i.py"
INFRA_MODEL_NAME="vic3d_latefusion_inf_imvoxelnet_973cefc0b2c14fee1b8775aa996ac779.pth"

VEHICLE_MODEL_PATH="../configs/vic3d/late-fusion-image/imvoxelnet"
VEHICLE_CONFIG_NAME="trainval_config_v.py"
VEHICLE_MODEL_NAME="vic3d_latefusion_veh_imvoxelnet_9d0ad4d4930c41d62839d45c06f86326.pth"

SPLIT_DATA_PATH="../data/split_datas/cooperative-split-data.json"

# srun --gres=gpu:a100:1 --time=1-0:0:0 --job-name "dair-v2x" \
CUDA_VISIBLE_DEVICES=$1
FUSION_METHOD=$2
DELAY_K=$3
EXTEND_RANGE_START=$4
EXTEND_RANGE_END=$5
TIME_COMPENSATION=$6
python eval.py \
  --input $DATA \
  --output $OUTPUT \
  --model $FUSION_METHOD \
  --dataset vic-async \
  --k $DELAY_K \
  --split val \
  --split-data-path $SPLIT_DATA_PATH \
  --inf-config-path $INFRA_MODEL_PATH/$INFRA_CONFIG_NAME \
  --inf-model-path $INFRA_MODEL_PATH/$INFRA_MODEL_NAME \
  --veh-config-path $VEHICLE_MODEL_PATH/$VEHICLE_CONFIG_NAME \
  --veh-model-path $VEHICLE_MODEL_PATH/${VEHICLE_MODEL_NAME} \
  --device ${CUDA_VISIBLE_DEVICES} \
  --pred-class car \
  --sensortype camera \
  --extended-range $EXTEND_RANGE_START -39.68 -3 $EXTEND_RANGE_END 39.68 1 \
  --overwrite-cache \
  $TIME_COMPENSATION