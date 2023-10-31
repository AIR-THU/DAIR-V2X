CUDA_VISIBLE_DEVICES=$1
DELAY_K=$2
EXTEND_RANGE_START=$3
EXTEND_RANGE_END=$4
TIME_COMPENSATION=$5
ONLY_DTC=$6

#Detection
DET_OUTPUT="../output/spd_late_camera/detection_results/"
if [ -d "$DET_OUTPUT" ]; then
    rm -r $DET_OUTPUT
fi

mkdir -p $DET_OUTPUT/result
mkdir -p $DET_OUTPUT/inf/camera
mkdir -p $DET_OUTPUT/veh/camera
bash scripts/eval_camera_late_fusion_imvoxelnet_spd.sh  \
        $CUDA_VISIBLE_DEVICES 'late_fusion' $DELAY_K $EXTEND_RANGE_START \
        $EXTEND_RANGE_END $TIME_COMPENSATION $DET_OUTPUT

echo "ONLY_DTC flag: "${ONLY_DTC}
if [ "$ONLY_DTC" != true ]; then
    #Tracking
    bash scripts/eval_camera_ab3dmot_spd.sh $DET_OUTPUT
fi
