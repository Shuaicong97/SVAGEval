# Step 1: from gt.json to gt.txt (spatial) and gt.jsonl (temporal). Only need to do once and saved
import os
import json
import time


def convert_query_string(query):
    return query.lower().replace(" ", "-")


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def process_spatial_ground_truth(queries, output_base):
    for query in queries:
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


def process_temporal_ground_truth(queries, output_dir, dataset_name):
    ensure_dir(output_dir)
    # output_path = os.path.join(output_dir, "ovis_valid.jsonl")
    output_path = os.path.join(output_dir, f"{dataset_name.lower()}_valid.jsonl")
    # with open(output_path, "r", encoding="utf-8") as f:
    #     ground_truth = json.load(f)
    all_qids = set()
    written_qids = set()
    results = []

    for query in queries:
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

            results.append({
                "qid": qid,
                "query": query_text,
                "duration": duration,
                "vid": vid,
                "track_id": track_id,
                "relevant_windows": new_relevant_windows,
                "relevant_clip_ids": relevant_clip_ids,
                "saliency_scores": saliency_scores
            })

            written_qids.add(qid)

    results.sort(key=lambda x: x["qid"])
    with open(output_path, "w", encoding="utf-8") as file:
        for item in results:
            file.write(json.dumps(item) + "\n")


def process_all_ground_truth(file_path, output_base):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for dataset in data["datasets"]:
        dataset_name = dataset["name"]  # e.g. OVIS, MOT17, MOT20
        queries = dataset["queries"]

        spatial_output_base = os.path.join(output_base, dataset_name, "spatial")
        temporal_output_base = os.path.join(output_base, dataset_name, "temporal")

        process_spatial_ground_truth(queries, spatial_output_base)
        process_temporal_ground_truth(queries, temporal_output_base, dataset_name)


def create_seqinfo(json_file, base_folder, dataset):
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

            if dataset == "ovis":
                seqinfo_content = f"""[Sequence]
name={file_name}
seqLength={length}
imWidth={width}
imHeight={height}
imExt=.png
"""
            if dataset == "mot17" or dataset == "mot20":
                frame_rate = item["frame_rate"]
                seqinfo_content = f"""[Sequence]
name={file_name}
imDir=img1
frameRate={frame_rate}
seqLength={length}
imWidth={width}
imHeight={height}
imExt=.jpg
"""

            with open(seqinfo_path, "w", encoding='utf-8') as seq_file:
                seq_file.write(seqinfo_content)
            count = count + 1
    print(f"Created {count} sequences")


start_time = time.time()

valid_all_gt = '../data/mot25-stag_valid_ground_truth.json'
output_base = '../data/gt'
process_all_ground_truth(valid_all_gt, output_base)

create_seqinfo("../data/length_ovis_valid.json", "../data/gt/OVIS/spatial", "ovis")
create_seqinfo("../data/length_mot.json", "../data/gt/MOT17/spatial", "mot17")
create_seqinfo("../data/length_mot.json", "../data/gt/MOT20/spatial", "mot20")

end_time = time.time()
print(f"Convert all gt in {end_time - start_time:.2f} seconds.")


def check_completeness(file_path, range_set):
    with open(file_path, "r") as f:
        qids_in_file = set(json.loads(line)["qid"] for line in f)
    missing_qids = sorted(set(range_set) - qids_in_file)

    if missing_qids:
        print(f"Missing QIDs ({len(missing_qids)}): {missing_qids}")
    else:
        print(f"All QIDs from {range_set} are present.")


file_path_ovis = os.path.join(output_base, 'OVIS/temporal/ovis_valid.jsonl')
file_path_mot17 = os.path.join(output_base, 'MOT17/temporal/mot17_valid.jsonl')
file_path_mot20 = os.path.join(output_base, 'MOT20/temporal/mot20_valid.jsonl')
check_completeness(file_path_ovis, range(5095, 5997))
check_completeness(file_path_mot17, range(782, 1281))
check_completeness(file_path_mot20, range(810, 1242))
