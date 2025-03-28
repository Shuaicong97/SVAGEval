# Need to be generated and saved forehand: SEQMAP_FILE, GT_FOLDER
python3 ../TrackEval/scripts/run_mot_challenge.py \
--METRICS HOTA \
--SEQMAP_FILE /Users/shuaicongwu/PycharmProjects/SVAGEval/data/seqmap_mini.txt \
--SKIP_SPLIT_FOL True \
--GT_FOLDER /Users/shuaicongwu/PycharmProjects/SVAGEval/data/gt/temporal/OVIS/val \
--TRACKERS_FOLDER /Users/shuaicongwu/PycharmProjects/SVAGEval/results \
--GT_LOC_FORMAT {gt_folder}{video_id}/{expression_id}/gt.txt \
--TRACKERS_TO_EVAL /Users/shuaicongwu/PycharmProjects/SVAGEval/results \
--USE_PARALLEL True \
--NUM_PARALLEL_CORES 2 \
--SKIP_SPLIT_FOL True \
--PLOT_CURVES False