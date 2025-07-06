#!/bin/bash
total_start=$(date +%s.%N)

convert_start=$(date +%s.%N)
echo "[Converting submission] ..."
INPUT_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/submission.json"
python3 convert_submission.py --input_file "${INPUT_FILE}"
convert_end=$(date +%s.%N)
convert_duration=$(awk -v start="$convert_start" -v end="$convert_end" 'BEGIN {print end - start}')
convert_formatted=$(printf "%.3f" "$convert_duration")
echo "✅ [convert_submission.py] done in $convert_formatted seconds"

echo "[Remove existing id_mapping json file] ..."
python3 run_svag.py --func remove

# Parameters must be listed in order
run_single_dataset() {
    local DATASET_NAME=$1

    local SEQMAP_FILE=$2
    local GT_FOLDER=$3
    local TRACKERS_FOLDER=$4
    local TRACKERS_TO_EVAL=$5

    local SUBMISSION_PATH=$6
    local GT_PATH=$7
    local SAVE_PATH=$8

    local SUMMARY=$9
    local COMBINED_RESULT_PATH=${10}

    echo "========== Running dataset: $DATASET_NAME =========="

    start=$(date +%s.%N)
    echo "[Spatial Evaluation] ..."
    sh ../spatial_eval/evaluate.sh "$SEQMAP_FILE" "$GT_FOLDER" "$TRACKERS_FOLDER" "$TRACKERS_TO_EVAL"

    echo "[Temporal Evaluation] ..."
    sh ../temporal_eval/eval.sh "$SUBMISSION_PATH" "$GT_PATH" "$SAVE_PATH"

    echo "[Combining results] ..."
    python3 run_svag.py --func combine --pedestrian_summary "$SUMMARY" --temporal_metrics "$SAVE_PATH" --combined_result_path "$COMBINED_RESULT_PATH"

    end=$(date +%s.%N)
    duration=$(awk -v start="$start" -v end="$end" 'BEGIN {print end - start}')
    formatted=$(printf "%.3f" "$duration")

    echo "✅ [$DATASET_NAME] done in $formatted seconds"
    echo ""
}

run_single_dataset "ovis" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/data_path/seqmap_ovis.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/OVIS/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/temporal/ovis_valid_preds.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/OVIS/temporal/ovis_valid.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/temporal/ovis_valid_preds_metrics.json" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/spatial/pedestrian_summary.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/combined_result_ovis.json"

run_single_dataset "mot17" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/data_path/seqmap_mot17.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/MOT17/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/temporal/mot17_valid_preds.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/MOT17/temporal/mot17_valid.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/temporal/mot17_valid_preds_metrics.json" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/spatial/pedestrian_summary.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/combined_result_mot17.json"

run_single_dataset "mot20" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/data_path/seqmap_mot20.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/MOT20/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/spatial" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/temporal/mot20_valid_preds.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/MOT20/temporal/mot20_valid.jsonl" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/temporal/mot20_valid_preds_metrics.json" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/spatial/pedestrian_summary.txt" \
    "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/combined_result_mot20.json"

OVIS_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/OVIS/combined_result_ovis.json"
MOT17_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT17/combined_result_mot17.json"
MOT20_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/MOT20/combined_result_mot20.json"
OUTPUT_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/predict/combined_result_mean.json"

echo "[Calculating average results] ..."
python3 average_combined_results.py --ovis_result "$OVIS_FILE" --mot17_result "$MOT17_FILE" --mot20_result "$MOT20_FILE" --average_result_path "$OUTPUT_FILE"

total_end=$(date +%s.%N)
total_duration=$(awk -v start="$total_start" -v end="$total_end" 'BEGIN {print end - start}')
total_formatted=$(printf "%.3f" "$total_duration")

echo "✅ All evaluations done in $total_formatted seconds"
echo ""