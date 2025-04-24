# Need to be generated and saved forehand: SEQMAP_FILE, GT_FOLDER
GT_FOLDER="$1"
TRACKERS_FOLDER="$2"
TRACKERS_TO_EVAL="$3"

echo "GT_FOLDER: $GT_FOLDER"
echo "TRACKERS_FOLDER: $TRACKERS_FOLDER"
echo "TRACKERS_TO_EVAL: $TRACKERS_TO_EVAL"

python3 ../TrackEval/scripts/run_mot_challenge.py \
--METRICS HOTA \
--SEQMAP_FILE /Users/shuaicongwu/PycharmProjects/SVAGEval/data/seqmap.txt \
--SKIP_SPLIT_FOL True \
--GT_FOLDER "$GT_FOLDER" \
--TRACKERS_FOLDER "$TRACKERS_FOLDER" \
--GT_LOC_FORMAT {gt_folder}{video_id}/{expression_id}/gt.txt \
--TRACKERS_TO_EVAL "$TRACKERS_TO_EVAL" \
--USE_PARALLEL True \
--NUM_PARALLEL_CORES 2 \
--SKIP_SPLIT_FOL True \
--PLOT_CURVES False