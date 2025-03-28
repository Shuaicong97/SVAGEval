import json
import os

# for MOT
def generate_gt_txt(submission_file, base_output_dir):
    with open(submission_file, "r") as file:
        data = json.load(file)

    created_video_dirs = set()
    for query in data["queries"]:
        qid = query["qid"]
        if not query["tracks"]:
            continue

        video_name = query["video_name"]
        video_dir = os.path.join(base_output_dir, video_name)
        if video_name not in created_video_dirs:
            os.makedirs(video_dir, exist_ok=True)
            created_video_dirs.add(video_name)

        qid_dir = os.path.join(video_dir, query["query"])
        os.makedirs(qid_dir, exist_ok=True)

        output_file = os.path.join(qid_dir, "predict.txt")
        predictions = []

        for track in query["tracks"]:
            track_id = track["track_id"]
            spatial = track["spatial"]
            temporal = track["temporal"]

            for time_range in temporal:
                if time_range[0] == time_range[1]:  # e.g. [2,2]
                    frame_ids = [time_range[0]]
                else: # e.g. [4,5]
                    frame_ids = list(range(time_range[0], time_range[1] + 1))

                for frame_id in frame_ids:
                    if spatial[frame_id - 1] is not None:
                        bbox = spatial[frame_id - 1]["bbox"]
                        x, y, width, height = bbox

                        row = (frame_id, int(track_id), float(x), float(y), float(width), float(height), 1, 1, 1)
                        predictions.append(row)

        # Sort by frame_id in ascending order. If frame_id is the same, sort by track_id.
        predictions.sort(key=lambda x: (x[0], x[1]))

        with open(output_file, "w") as f:
            for row in predictions:
                f.write(",".join(map(str, row)) + "\n")

        print(f"Saved predict bbox to {output_file}")

# for Temporal Grounding
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = [[float(start), float(end)] for start, end in intervals]
    intervals.sort()
    merged = [list(intervals[0])]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1] + 1:
            last[1] = max(last[1], current[1])
        else:
            merged.append(list(current))
    return merged

def generate_predict_dict(submission_file, output_dir):
    with open(submission_file, "r") as file:
        data = json.load(file)

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "sample_preds.jsonl")

    with open(output_file, "w") as f:
        for query in data["queries"]:
            for track in query["tracks"]:
                temporal = track["temporal"]
                scores = track["score"]

                pred_relevant_windows = [
                    [float(start), float(end), float(score)]
                    for (start, end), score in zip(temporal, scores)
                ]

                output_entry = {
                    "qid": query["qid"],
                    "query": query["query"],
                    "vid": query["video_id"],
                    "video_name": query["video_name"],
                    "track_id": track["track_id"],
                    "pred_relevant_windows": pred_relevant_windows
                }
                f.write(json.dumps(output_entry) + "\n")

    print(f"Saved predict dict to {output_file}")
