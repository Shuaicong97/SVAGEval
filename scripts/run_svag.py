import argparse
from convert_submission import process_spatial_predictions, process_temporal_predictions
import json
import os

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

    parser.add_argument('--input_file', type=str, default='../data/mock_submission.json', help='submission json file')
    parser.add_argument('--eval_dir', type=str, default='../results/evaluation', help='path to the evaluation result')
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

    args = parser.parse_args()

    if args.combine_only:
        combine_evaluation_results(args.pedestrian_summary, args.temporal_metrics, args.combined_result_path)
    else:
        # First, the uploaded file must be converted into a format that can be evaluated in both dimensions.
        # gt format in spatial, jsonl format in temporal
        process_spatial_predictions(args.input_file, args.convert_results_in_spatial_dir)
        process_temporal_predictions(args.input_file, args.convert_results_in_temporal_dir)