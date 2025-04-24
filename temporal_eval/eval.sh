# Usage: bash temporal_eval/eval.sh
cd "$(dirname "$0")"

SUBMISSION_PATH="$1"
GT_PATH="$2"
SAVE_PATH="$3"

echo "SUBMISSION_PATH: $SUBMISSION_PATH"
echo "GT_PATH: $GT_PATH"
echo "SAVE_PATH: $SAVE_PATH"

python3 eval.py \
--submission_path "$SUBMISSION_PATH" \
--gt_path "$GT_PATH" \
--save_path "$SAVE_PATH"
