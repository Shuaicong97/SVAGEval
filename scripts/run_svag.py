import argparse
from convert_submission import process_spatial_predictions, process_temporal_predictions
from convert_valid_gt import process_spatial_ground_truth, process_temporal_ground_truth, create_seqinfo
import json
import os

# only need to do once
def prepare_ground_truth_if_needed(gt_json, spatial_output_base, temporal_output_dir):
    # simple way: only to check temporal.jsonl, if not exists, run all three functions
    temporal_output_file = os.path.join(temporal_output_dir, "ovis_valid.jsonl")
    if not os.path.exists(temporal_output_file):
        print(f"[INFO] Temporal GT not found, run all three functions")
        process_spatial_ground_truth(gt_json, spatial_output_base)
        process_temporal_ground_truth(gt_json, temporal_output_dir)
        video_info_path = "/Users/shuaicongwu/PycharmProjects/SVAGEval/data/video_info_valid.json"
        create_seqinfo(video_info_path, spatial_output_base)
    else:
        print(f"[✓] All ground truth data are converted, skipping.")


def combine_evaluation_results(spatial_results, temporal_results, output_path):
    with open(spatial_results, 'r') as f:
        keys = f.readline().strip().split()
        values = list(map(float, f.readline().strip().split()))
        spatial_data = dict(zip(keys, values))

    with open(temporal_results, 'r') as f:
        temporal_data = json.load(f)

    result = {
        "result": {
            "spatial": spatial_data,
            "temporal": temporal_data
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=4)

    print(f"Combined result is saved to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SVAG Evaluation Script")

    parser.add_argument('--input_file', type=str, default='', help='Submission json file')
    parser.add_argument('--eval_dir', type=str, default='../results/evaluation', help='Path to the evaluation result')
    parser.add_argument('--convert_results_in_spatial_dir', type=str, default='../data/ovis_prediction/spatial',
                        help="Path to the spatial predictions")
    parser.add_argument('--convert_results_in_temporal_dir', type=str, default='../data/ovis_prediction/temporal',
                        help="Path to the temporal predictions")
    parser.add_argument('--pedestrian_summary', type=str, default='../data/ovis_prediction/spatial/pedestrian_summary.txt',
                        help='Path to pedestrian_summary.txt')
    parser.add_argument('--temporal_metrics', type=str, default='../data/ovis_prediction/temporal/ovis_val_preds_metrics.json',
                        help='Path to temporal ovis_val_preds_metrics.json file')
    parser.add_argument('--combined_result_path', type=str, default='../data/ovis_prediction/combined_result.json',
                        help='Path to combined_result file')
    parser.add_argument('--combine_only', action='store_true', help='Only combine evaluation results')
    parser.add_argument('--ovis_gt_file', type=str,
                        default='/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_valid_ground_truth.json', help='OVIS valid gt file')
    parser.add_argument('--spatial_output_base', type=str,
                        default='/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/spatial/valid', help='Path to gt spatial output directory')
    parser.add_argument('--temporal_output_dir', type=str,
                        default='/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/temporal', help='Path to gt temporal output directory')

    args = parser.parse_args()

    if args.combine_only:
        combine_evaluation_results(args.pedestrian_summary, args.temporal_metrics, args.combined_result_path)
    else:
        # First, the uploaded file must be converted into a format that can be evaluated in both dimensions.
        # gt format in spatial, jsonl format in temporal
        prepare_ground_truth_if_needed(args.ovis_gt_file, args.spatial_output_base, args.temporal_output_dir)
        process_spatial_predictions(args.input_file, args.convert_results_in_spatial_dir)
        process_temporal_predictions(args.input_file, args.convert_results_in_temporal_dir)
