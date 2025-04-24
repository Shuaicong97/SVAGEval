# Usage: bash scripts/run_svag.sh
# spatial path definition
#SEQMAP_FILE=""
INPUT_FILE="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/submission.json"
GT_FOLDER="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/spatial/valid"
TRACKERS_FOLDER="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_prediction/spatial"
TRACKERS_TO_EVAL="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_prediction/spatial"
# temporal path definition
SUBMISSION_PATH="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_prediction/temporal/ovis_valid_preds.jsonl"
GT_PATH="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/temporal/ovis_valid.jsonl"
SAVE_PATH="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_prediction/temporal/ovis_val_preds_metrics.json"

while [[ "$#" -gt 0 ]]; do
    case $1 in
#        --SEQMAP_FILE) SEQMAP_FILE="$2"; shift ;;
        --input_file) INPUT_FILE="$2"; shift ;;
        --GT_FOLDER) GT_FOLDER="$2"; shift ;;
        --TRACKERS_FOLDER) TRACKERS_FOLDER="$2"; shift ;;
        --TRACKERS_TO_EVAL) TRACKERS_TO_EVAL="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

python3 run_svag.py --input_file "${INPUT_FILE}"

# Run spatial and temporal eval. Need to change their arguments in the files
sh ../spatial_eval/evaluate.sh "${GT_FOLDER}" "${TRACKERS_FOLDER}" "${TRACKERS_TO_EVAL}"
sh ../temporal_eval/eval.sh "${SUBMISSION_PATH}" "${GT_PATH}" "${SAVE_PATH}"

python3 run_svag.py --combine_only
