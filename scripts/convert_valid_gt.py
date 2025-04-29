# Step 1: from gt.json to gt.txt (spatial) and gt.jsonl (temporal). Only need to do once and saved
import os
import json

def convert_query_string(query):
    return query.lower().replace(" ", "-")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_spatial_ground_truth(file_path, output_base="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/spatial/valid"):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for query in data["queries"]:
        video_name = query["video_name"]
        query_str = query["query"]
        tracks = query["tracks"]

        converted_query = convert_query_string(query_str)
        output_dir = os.path.join(output_base, video_name, converted_query)
        ensure_dir(output_dir)
        gt_file_path = os.path.join(output_dir, "gt.txt")

        with open(gt_file_path, "w") as gt_file:
            for track in tracks:
                track_id = track["track_id"]
                spatial = track["spatial"]

                for idx, box in enumerate(spatial):
                    if box is not None:
                        x, y, w, h = box
                        frame_id = idx + 1  # Index starts at 1
                        gt_file.write(f"{frame_id}, {track_id}, {x}, {y}, {w}, {h}, 1, 1, 1\n")

def process_temporal_ground_truth(file_path, output_dir="/Users/shuaicongwu/PycharmProjects/SVAGEval/data/ovis_gt/temporal"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ovis_valid.jsonl")

    with open(file_path, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    with open(output_path, "w", encoding="utf-8") as file:
        for query in ground_truth["queries"]:
            qid = query["query_id"]
            query_text = query["query"]
            duration = query["video_length"]
            video_name = query["video_name"]
            vid = f"{video_name}_1.0_{duration}.0"

            for track in query["tracks"]:
                track_id = track["track_id"]
                relevant_windows = track["temporal"]
                relevant_clip_ids = []
                new_relevant_windows = []

                for window in relevant_windows:
                    if window is None:
                        continue
                    # they are from the img name
                    start, end = window

                    if video_name == "cfff47c3":
                        start = start - 170 - 1
                        end = end - 170
                    elif video_name == "af48b2f9":
                        if start <= 5:
                            start -= 1

                        if start == 8:
                            start = 6 - 1
                        if end == 8:
                            end = 6

                        if start >= 12:
                            start = start - 5 - 1
                        if end >= 12:
                            end = end - 5
                    else:
                        start -= 1

                    new_relevant_windows.append([start, end])

                    clip_start = start // 2
                    clip_end = (end - 1) // 2
                    clip_ids = list(range(clip_start, clip_end + 1))
                    relevant_clip_ids.extend(clip_ids)

                relevant_clip_ids = sorted(set(relevant_clip_ids))
                saliency_scores = [[4, 4, 4] for _ in relevant_clip_ids]

                json_line = {
                    "qid": qid,
                    "query": query_text,
                    "duration": duration,
                    "vid": vid,
                    "track_id": track_id,
                    "relevant_windows": new_relevant_windows,
                    "relevant_clip_ids": relevant_clip_ids,
                    "saliency_scores": saliency_scores
                }

                file.write(json.dumps(json_line) + "\n")

def create_seqinfo(json_file, base_folder):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for item in data:
        file_name = item["file_name"]
        width = item["width"]
        height = item["height"]
        length = item["length"]

        target_folder = os.path.join(base_folder, file_name)

        if os.path.isdir(target_folder):
            seqinfo_path = os.path.join(target_folder, "seqinfo.ini")
            seqinfo_content = f"""[Sequence]
name={file_name}
seqLength={length}
imWidth={width}
imHeight={height}
imExt=.png
"""

            with open(seqinfo_path, "w", encoding='utf-8') as seq_file:
                seq_file.write(seqinfo_content)
            count = count + 1
    print(f"Created {count} sequences")
