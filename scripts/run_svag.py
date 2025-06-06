import argparse
import json
import os


def remove_id_mapping(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")


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
    parser.add_argument('--func', type=str, required=True, help="Function to run: remove or combine")
    parser.add_argument('--pedestrian_summary', type=str, default='', help='Path to pedestrian_summary.txt')
    parser.add_argument('--temporal_metrics', type=str, default='',
                        help='Path to temporal valid_preds_metrics.json file')
    parser.add_argument('--combined_result_path', type=str, default='', help='Path to combined_result file')
    parser.add_argument("--id_mapping_path", type=str, default='../results/id_mapping.jsonl',
                        help="path to id mapping file generated from MOT gt-prediction id matching, equals to SAVE_PATH defined in trackeval/eval")

    args = parser.parse_args()

    if args.func == 'remove':
        remove_id_mapping(args.id_mapping_path)
    elif args.func == 'combine':
        combine_evaluation_results(args.pedestrian_summary, args.temporal_metrics, args.combined_result_path)
