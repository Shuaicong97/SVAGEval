import argparse
import json
import os


def remove_id_mapping(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")

def parse_summary_txt(summary_path):
    with open(summary_path, 'r') as f:
        lines = f.readlines()

    headers = lines[0].strip().split()
    values = list(map(float, lines[1].strip().split()))
    summary_data = dict(zip(headers, values))

    keys_needed = ["HOTA", "DetA", "AssA", "DetRe", "DetPr", "AssRe", "AssPr", "LocA"]
    extracted = {k: summary_data[k] for k in keys_needed if k in summary_data}
    return extracted

def parse_metrics_json(metrics_path):
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    brief = metrics["brief"]
    rename_map = {
        "MR-full-mIoU": "mIoU",
        "MR-full-R1@0.1": "R1@0.1",
        "MR-full-R1@0.3": "R1@0.3",
        "MR-full-R1@0.5": "R1@0.5",
        "MR-full-R5@0.1": "R5@0.1",
        "MR-full-R5@0.3": "R5@0.3",
        "MR-full-R5@0.5": "R5@0.5",
        "MR-full-R10@0.1": "R10@0.1",
        "MR-full-R10@0.3": "R10@0.3",
        "MR-full-R10@0.5": "R10@0.5"
    }

    extracted = {new_key: brief[old_key] for old_key, new_key in rename_map.items() if old_key in brief}
    return extracted


def combine_evaluation_results(spatial_results, temporal_results, output_path):
    result = {}
    result.update(parse_summary_txt(spatial_results))
    result.update(parse_metrics_json(temporal_results))

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
