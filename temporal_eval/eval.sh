# Usage: bash temporal_eval/eval.sh
cd "$(dirname "$0")"

submission_path=sample_val_preds_no_saliency_scores.jsonl
gt_path=../data/ovis_val_release.jsonl
save_path=sample_val_preds_metrics-nosortscore.json

python3 eval.py \
--submission_path ${submission_path} \
--gt_path ${gt_path} \
--save_path ${save_path}
