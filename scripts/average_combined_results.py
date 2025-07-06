import json
import sys
import os
import argparse
from collections import OrderedDict


def load_result(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def average_dicts(dicts):
    avg = {}
    for key in dicts[0]:
        if isinstance(dicts[0][key], dict):
            avg[key] = average_dicts([d[key] for d in dicts])
        else:
            avg[key] = round(sum(d[key] for d in dicts) / len(dicts), 3)
    return avg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Average combined results")
    parser.add_argument('--ovis_result', type=str, default='', help='OVIS combined result json file')
    parser.add_argument('--mot17_result', type=str, default='', help='MOT17 combined result json file')
    parser.add_argument('--mot20_result', type=str, default='', help='MOT20 combined result json file')
    parser.add_argument('--average_result_path', type=str, default='',
                        help="Path to the average combined result json file")

    args = parser.parse_args()

    single_files = [args.ovis_result, args.mot17_result, args.mot20_result]
    output_path = args.average_result_path
    if not all(os.path.exists(f) for f in single_files):
        print("No such file or directory in: {}".format(single_files))
        sys.exit(1)

    results = [load_result(f) for f in single_files]
    mean_result = average_dicts(results)

    try:
        hota = mean_result.get("HOTA", None)
        miou = mean_result.get("mIoU", None)
        if hota is not None and miou is not None:
            m_hiou = round((hota + miou) / 2, 3)
        else:
            raise ValueError("Missing 'HOTA' or 'mIoU' key in averaged result.")
    except Exception as e:
        print(f"❌ Failed to calculate m-HIoU: {e}")
        sys.exit(1)

    ordered_result = OrderedDict()
    ordered_result["m-HIoU"] = m_hiou
    for k, v in mean_result.items():
        ordered_result[k] = v

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ordered_result, f, indent=4)

    print(f"✅ final average result saved in: {output_path}")
