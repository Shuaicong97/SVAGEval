import argparse
import json
import os
import time
from convert_submission import *
import subprocess
from average_combined_results import *


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

def run_spatial_eval(seqmap_file, gt_folder, trackers_folder, trackers_to_eval):
    cmd = [
        "sh", "../spatial_eval/evaluate.sh",
        seqmap_file,
        gt_folder,
        trackers_folder,
        trackers_to_eval
    ]
    try:
        subprocess.run(cmd, check=True)
        print("✅ Spatial evaluation finished.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during spatial evaluation: {e}")

def run_temporal_eval(submission_path, gt_path, save_path):
    cmd = [
        "sh", "../temporal_eval/eval.sh",
        submission_path,
        gt_path,
        save_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print("✅ Temporal evaluation finished.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during temporal evaluation: {e}")

def run_single_dataset(dataset_name, seqmap_file, gt_folder, trackers_folder, trackers_to_eval,
                       submission_path, gt_path, save_path, summary, combined_result_path):
    print(f"========== Running dataset: {dataset_name} ==========")
    start = time.time()
    print(f"[Spatial Evaluation] ...")
    run_spatial_eval(seqmap_file, gt_folder, trackers_folder, trackers_to_eval)
    print(f"[Temporal Evaluation] ...")
    run_temporal_eval(submission_path, gt_path, save_path)
    print(f"[Combining results] ...")
    combine_evaluation_results(summary, save_path, combined_result_path)
    end = time.time()
    duration = end - start
    print(f"{dataset_name} in {duration:.2f} seconds")


def main(args):
    total_start = time.time()
    # 1. Converting submission
    process_all_preditions(args.submission_file)

    # 2. Remove existing id_mapping json file
    remove_id_mapping(args.id_mapping_path)

    # 3. Run single dataset evaluation
    run_single_dataset('ovis', '../data/data_path/seqmap_ovis.txt',
                       '../data/gt/OVIS/spatial', '../data/predict/OVIS/spatial',
                       '../data/predict/OVIS/spatial', '../data/predict/OVIS/temporal/ovis_valid_preds.jsonl',
                       '../data/gt/OVIS/temporal/ovis_valid.jsonl', '../data/predict/OVIS/temporal/ovis_valid_preds_metrics.json',
                       '../data/predict/OVIS/data/predict/OVIS/spatial/pedestrian_summary.txt', args.ovis_result)
    run_single_dataset('mot17', '../data/data_path/seqmap_mot17.txt',
                       '../data/gt/MOT17/spatial', '../data/predict/MOT17/spatial',
                       '../data/predict/MOT17/spatial', '../data/predict/MOT17/temporal/mot17_valid_preds.jsonl',
                       '../data/gt/MOT17/temporal/mot17_valid.jsonl', '../data/predict/MOT17/temporal/mot17_valid_preds_metrics.json',
                       '../data/predict/MOT17/data/predict/MOT17/spatial/pedestrian_summary.txt', args.mot17_result)
    run_single_dataset('mot20', '../data/data_path/seqmap_mot20.txt',
                       '../data/gt/MOT20/spatial', '../data/predict/MOT20/spatial',
                       '../data/predict/MOT20/spatial', '../data/predict/MOT20/temporal/mot20_valid_preds.jsonl',
                       '../data/gt/MOT20/temporal/mot20_valid.jsonl', '../data/predict/MOT20/temporal/mot20_valid_preds_metrics.json',
                       '../data/predict/MOT20/data/predict/MOT20/spatial/pedestrian_summary.txt', args.mot20_result)

    # 4. Calculate the mean
    subprocess.run(["python3", "average_combined_results.py",
                    "--ovis_result", args.ovis_result,
                    "--mot17_result", args.mot17_result,
                    "--mot20_result", args.mot20_result,
                    "--average_result_path", args.final_result
                    ])

    total_end = time.time()
    total_duration = total_end - total_start
    print(f"✅ All evaluations done in {total_duration:.2f} seconds")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SVAG Evaluation Script")
    parser.add_argument("--id_mapping_path", type=str, default='../results/id_mapping.jsonl',
                        help="path to id mapping file generated from MOT gt-prediction id matching, equals to SAVE_PATH defined in trackeval/eval")
    parser.add_argument('--submission_file', type=str, default='../data/submission.json', help='Path to submission file')
    parser.add_argument('--ovis_result', type=str, default='../data/predict/OVIS/combined_result.json', help='Path to ovis result')
    parser.add_argument('--mot17_result', type=str, default='../data/predict/MOT17/combined_result.json', help='Path to mot17 result')
    parser.add_argument('--mot20_result', type=str, default='../data/predict/MOT20/combined_result.json', help='Path to mot20 result')
    parser.add_argument('--final_result', type=str, default='../data/predict/combined_result_mean.json', help='Path to the final average result')

    args = parser.parse_args()
    main(args)
