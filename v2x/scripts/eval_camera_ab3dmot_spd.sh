#Tracking
DET_OUTPUT=$1

SPLIT_DATA_PATH="../data/split_datas/cooperative-split-data-spd.json"
DATASET='KITTI'
SPLIT='val'
TYPE='Car'
DETNAME='imvoxelnet'
EVAL_RESULT_NAME='spd_late_camera'

#Convert detection results to KITTI format
OUTPUT_PATH_DTC="../output/${EVAL_RESULT_NAME}/detection_results_to_kitti"
OUTPUT_PATH_DTC_SUB="${OUTPUT_PATH_DTC}/${DETNAME}_${TYPE}_${SPLIT}"

mkdir -p $OUTPUT_PATH_DTC_SUB
python ../tools/dataset_converter/label_det_result2kitti.py \
  --input-dir-path ${DET_OUTPUT}/result \
  --output-dir-path ${OUTPUT_PATH_DTC_SUB} \
  --spd-path ../data/V2X-Seq-SPD

#AB3DMOT
INPUT_PATH_TRACK=$OUTPUT_PATH_DTC
OUTPUT_PATH_TRACK="../output/${EVAL_RESULT_NAME}/tracking_results_to_kitti"

mkdir -p $OUTPUT_PATH_TRACK
python AB3DMOT_plugin/main_tracking.py \
  --dataset $DATASET \
  --split $SPLIT \
  --det_name $DETNAME \
  --cat $TYPE \
  --split-data-path $SPLIT_DATA_PATH \
  --input-path $INPUT_PATH_TRACK  \
  --output-path $OUTPUT_PATH_TRACK

#Eval
TRACK_EVAL_GT_PATH="../data/V2X-Seq-SPD-KITTI"
TRACK_EVAL_OUTPUT_PATH="../output/${EVAL_RESULT_NAME}/tracking_evaluation_results"
FUSION_METHOD="late_fusion"
python eval_tracking.py \
  --track-eval-gt-path $TRACK_EVAL_GT_PATH \
  --track-results-path $OUTPUT_PATH_TRACK \
  --track-eval-output-path $TRACK_EVAL_OUTPUT_PATH \
  --split $SPLIT \
  --det-name $DETNAME \
  --cat $TYPE \
  --fusion-method $FUSION_METHOD \
