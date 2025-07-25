"""
compute_mr_r5() function from https://github.com/showlab/UniVTG/blob/32659ac7aeba21742a63274f30eba785fc57e247/eval/eval.py
"""
import numpy as np
from collections import OrderedDict, defaultdict
import json
import time
import copy
import multiprocessing as mp

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporal_eval.utils import compute_average_precision_detection, \
    compute_temporal_iou_batch_cross, compute_temporal_iou_batch_paired, load_jsonl, get_ap


def compute_average_precision_detection_wrapper(
        input_triple, tiou_thresholds=np.linspace(0.5, 0.95, 10)):
    qid, ground_truth, prediction = input_triple
    scores = compute_average_precision_detection(
        ground_truth, prediction, tiou_thresholds=tiou_thresholds)
    return qid, scores


def compute_mr_ap(submission, ground_truth, iou_thds=np.linspace(0.1, 0.95, 18),
                  max_gt_windows=None, max_pred_windows=10, num_workers=8, chunksize=50):
    iou_thds = [float(f"{e:.2f}") for e in iou_thds]
    pred_qid2data = defaultdict(list)
    for d in submission:
        pred_windows = d["pred_relevant_windows"][:max_pred_windows] \
            if max_pred_windows is not None else d["pred_relevant_windows"]
        qid = d["qid"]
        for w in pred_windows:
            pred_qid2data[qid].append({
                "video-id": d["qid"],  # in order to use the API
                "t-start": w[0],
                "t-end": w[1],
                "score": w[2]
            })

    gt_qid2data = defaultdict(list)
    for d in ground_truth:
        gt_windows = d["relevant_windows"][:max_gt_windows] \
            if max_gt_windows is not None else d["relevant_windows"]
        qid = d["qid"]
        for w in gt_windows:
            gt_qid2data[qid].append({
                "video-id": d["qid"],
                "t-start": w[0],
                "t-end": w[1]
            })
    qid2ap_list = {}
    # start_time = time.time()
    data_triples = [[qid, gt_qid2data[qid], pred_qid2data[qid]] for qid in pred_qid2data]
    from functools import partial
    compute_ap_from_triple = partial(
        compute_average_precision_detection_wrapper, tiou_thresholds=iou_thds)

    if num_workers > 1:
        with mp.Pool(num_workers) as pool:
            for qid, scores in pool.imap_unordered(compute_ap_from_triple, data_triples, chunksize=chunksize):
                qid2ap_list[qid] = scores
    else:
        for data_triple in data_triples:
            qid, scores = compute_ap_from_triple(data_triple)
            qid2ap_list[qid] = scores

    # print(f"compute_average_precision_detection {time.time() - start_time:.2f} seconds.")
    ap_array = np.array(list(qid2ap_list.values()))  # (#queries, #thd)
    ap_thds = ap_array.mean(0)  # mAP at different IoU thresholds.
    iou_thd2ap = dict(zip([str(e) for e in iou_thds], ap_thds))
    iou_thd2ap["average"] = np.mean(ap_thds)
    # formatting
    iou_thd2ap = {k: float(f"{100 * v:.2f}") for k, v in iou_thd2ap.items()}
    return iou_thd2ap


def compute_mr_r1(submission, ground_truth, iou_thds=np.linspace(0.1, 0.95, 18)):
    """If a predicted segment has IoU >= iou_thd with one of the 1st GT segment, we define it positive"""
    iou_thds = [float(f"{e:.2f}") for e in iou_thds]
    pred_qid2window = {d["qid"]: d["pred_relevant_windows"][0][:2] for d in submission}  # :2 rm scores
    # gt_qid2window = {d["qid"]: d["relevant_windows"][0] for d in ground_truth}
    gt_qid2window = {}
    for d in ground_truth:
        cur_gt_windows = d["relevant_windows"]
        cur_qid = d["qid"]
        cur_max_iou_idx = 0
        if len(cur_gt_windows) > 0:  # select the GT window that has the highest IoU
            cur_ious = compute_temporal_iou_batch_cross(
                np.array([pred_qid2window[cur_qid]]), np.array(d["relevant_windows"])
            )[0]
            cur_max_iou_idx = np.argmax(cur_ious)
        gt_qid2window[cur_qid] = cur_gt_windows[cur_max_iou_idx]

    qids = list(pred_qid2window.keys())
    pred_windows = np.array([pred_qid2window[k] for k in qids]).astype(float)
    gt_windows = np.array([gt_qid2window[k] for k in qids]).astype(float)
    pred_gt_iou = compute_temporal_iou_batch_paired(pred_windows, gt_windows)
    iou_thd2recall_at_one = {}
    miou_at_one = float(f"{np.mean(pred_gt_iou) * 100:.2f}")
    for thd in iou_thds:
        iou_thd2recall_at_one[str(thd)] = float(f"{np.mean(pred_gt_iou >= thd) * 100:.2f}")
    return iou_thd2recall_at_one, miou_at_one


def compute_mr_r5(submission, ground_truth, iou_thds=np.linspace(0.1, 0.95, 18)):
    """If a predicted segment has IoU >= iou_thd with one of the 1st GT segment, we define it positive"""
    iou_thds = [float(f"{e:.2f}") for e in iou_thds]
    pred_qid2window = {d["qid"]: [x[:2] for x in d["pred_relevant_windows"][:5]] for d in submission}
    gt_qid2window = {}
    pred_optimal_qid2window = {}
    for d in ground_truth:
        cur_gt_windows = d["relevant_windows"]
        cur_qid = d["qid"]
        cur_max_iou_pred = 0
        cur_max_iou_gt = 0
        # cur_max_iou_idx = 0
        if len(cur_gt_windows) > 0:
            try:
                cur_ious = compute_temporal_iou_batch_cross(
                    np.array(pred_qid2window[cur_qid]), np.array(d["relevant_windows"])
                )[0]
                # replace all NaN to 0
                cur_ious[np.isnan(cur_ious)] = 0
                cur_max_iou_pred, cur_max_iou_gt = np.where(cur_ious == np.max(cur_ious))
                cur_max_iou_pred, cur_max_iou_gt = cur_max_iou_pred[0], cur_max_iou_gt[0]
            except:
                print(f"error happen when `cur_ious' equal to {cur_ious}")
        pred_optimal_qid2window[cur_qid] = pred_qid2window[cur_qid][cur_max_iou_pred]
        gt_qid2window[cur_qid] = cur_gt_windows[cur_max_iou_gt]

    qids = list(pred_qid2window.keys())
    pred_windows = np.array([pred_optimal_qid2window[k] for k in qids]).astype(float)
    gt_windows = np.array([gt_qid2window[k] for k in qids]).astype(float)
    pred_gt_iou = compute_temporal_iou_batch_paired(pred_windows, gt_windows)
    iou_thd2recall_at_five = {}
    miou_at_five = float(f"{np.mean(pred_gt_iou) * 100:.2f}")
    for thd in iou_thds:
        iou_thd2recall_at_five[str(thd)] = float(f"{np.mean(pred_gt_iou >= thd) * 100:.2f}")
    return iou_thd2recall_at_five, miou_at_five


def compute_mr_r10(submission, ground_truth, iou_thds=np.linspace(0.1, 0.95, 18)):
    """If a predicted segment has IoU >= iou_thd with one of the 1st GT segment, we define it positive"""
    iou_thds = [float(f"{e:.2f}") for e in iou_thds]
    pred_qid2window = {d["qid"]: [x[:2] for x in d["pred_relevant_windows"][:10]] for d in submission}
    gt_qid2window = {}
    pred_optimal_qid2window = {}
    for d in ground_truth:
        cur_gt_windows = d["relevant_windows"]
        cur_qid = d["qid"]
        cur_max_iou_pred = 0
        cur_max_iou_gt = 0
        # cur_max_iou_idx = 0
        if len(cur_gt_windows) > 0:
            try:
                cur_ious = compute_temporal_iou_batch_cross(
                    np.array(pred_qid2window[cur_qid]), np.array(d["relevant_windows"])
                )[0]
                # replace all NaN to 0
                cur_ious[np.isnan(cur_ious)] = 0
                cur_max_iou_pred, cur_max_iou_gt = np.where(cur_ious == np.max(cur_ious))
                cur_max_iou_pred, cur_max_iou_gt = cur_max_iou_pred[0], cur_max_iou_gt[0]
            except:
                print(f"error happen when `cur_ious' equal to {cur_ious}")
        pred_optimal_qid2window[cur_qid] = pred_qid2window[cur_qid][cur_max_iou_pred]
        gt_qid2window[cur_qid] = cur_gt_windows[cur_max_iou_gt]

    qids = list(pred_qid2window.keys())
    pred_windows = np.array([pred_optimal_qid2window[k] for k in qids]).astype(float)
    gt_windows = np.array([gt_qid2window[k] for k in qids]).astype(float)
    pred_gt_iou = compute_temporal_iou_batch_paired(pred_windows, gt_windows)
    iou_thd2recall_at_ten = {}
    miou_at_ten = float(f"{np.mean(pred_gt_iou) * 100:.2f}")
    for thd in iou_thds:
        iou_thd2recall_at_ten[str(thd)] = float(f"{np.mean(pred_gt_iou >= thd) * 100:.2f}")
    return iou_thd2recall_at_ten, miou_at_ten


def get_window_len(window):
    return window[1] - window[0]


def get_data_by_range(submission, ground_truth, len_range):
    """ keep queries with ground truth window length in the specified length range.
    Args:
        submission:
        ground_truth:
        len_range: [min_l (int), max_l (int)]. the range is (min_l, max_l], i.e., min_l < l <= max_l
    """
    min_l, max_l = len_range
    if min_l == 0 and max_l == 9999:  # first change max_l based on each dict duration
        for d in ground_truth:
            max_l = d['duration']

    # only keep ground truth with windows in the specified length range
    # if multiple GT windows exists, we only keep the ones in the range
    ground_truth_in_range = []
    gt_qids_in_range = set()
    for d in ground_truth:
        rel_windows_in_range = [
            w for w in d["relevant_windows"] if min_l < get_window_len(w) <= max_l]
        print(f'rel_windows_in_range: {rel_windows_in_range}')
        if len(rel_windows_in_range) > 0:
            d = copy.deepcopy(d)
            d["relevant_windows"] = rel_windows_in_range
            ground_truth_in_range.append(d)
            gt_qids_in_range.add(d["qid"])

    # keep only submissions for ground_truth_in_range
    submission_in_range = []
    for d in submission:
        if d["qid"] in gt_qids_in_range:
            submission_in_range.append(copy.deepcopy(d))

    return submission_in_range, ground_truth_in_range


def eval_moment_retrieval(submission, ground_truth, verbose=True):
    ret_metrics = {}
    if verbose:
        start_time = time.time()

    if len(ground_truth) == 0:
        # ret_metrics[name] = {"MR-mAP": 0., "MR-R1": 0.}
        dummy_dict = {}
        for k in np.linspace(0.5, 0.95, 19):
            dummy_dict[k] = 0.
        dummy_dict['average'] = 0.
        ret_metrics['full'] = {"MR-mAP": dummy_dict, "MR-R1": dummy_dict}
    else:
        iou_thd2average_precision = compute_mr_ap(submission, ground_truth, num_workers=8, chunksize=50)
        iou_thd2recall_at_one, miou_at_one = compute_mr_r1(submission, ground_truth)
        iou_thd2recall_at_five, miou_at_five = compute_mr_r5(submission, ground_truth)
        iou_thd2recall_at_ten, miou_at_ten = compute_mr_r10(submission, ground_truth)
        ret_metrics['full'] = {"MR-mIoU": miou_at_one,
                               "MR-mAP": iou_thd2average_precision,
                               "MR-R1": iou_thd2recall_at_one,
                               "MR-R5": iou_thd2recall_at_five,
                               "MR-R10": iou_thd2recall_at_ten}

        # iou_thd2average_precision = compute_mr_ap(_submission, _ground_truth, num_workers=8, chunksize=50)
        # iou_thd2recall_at_one = compute_mr_r1(_submission, _ground_truth)
        # ret_metrics[name] = {"MR-mAP": iou_thd2average_precision, "MR-R1": iou_thd2recall_at_one}
        if verbose:
            print(f"[eval_moment_retrieval] [full] {time.time() - start_time:.2f} seconds")
    return ret_metrics


def compute_hl_hit1(qid2preds, qid2gt_scores_binary):
    qid2max_scored_clip_idx = {k: np.argmax(v["pred_saliency_scores"]) for k, v in qid2preds.items()}
    hit_scores = np.zeros((len(qid2preds), 3))
    qids = list(qid2preds.keys())
    for idx, qid in enumerate(qids):
        pred_clip_idx = qid2max_scored_clip_idx[qid]
        gt_scores_binary = qid2gt_scores_binary[qid]  # (#clips, 3)
        if pred_clip_idx < len(gt_scores_binary):
            hit_scores[idx] = gt_scores_binary[pred_clip_idx]
    # aggregate scores from 3 separate annotations (3 workers) by taking the max.
    # then average scores from all queries.
    hit_at_one = float(f"{100 * np.mean(np.max(hit_scores, 1)):.2f}")
    return hit_at_one


def compute_hl_ap(qid2preds, qid2gt_scores_binary, num_workers=8, chunksize=50):
    qid2pred_scores = {k: v["pred_saliency_scores"] for k, v in qid2preds.items()}
    ap_scores = np.zeros((len(qid2preds), 3))  # (#preds, 3)
    qids = list(qid2preds.keys())
    input_tuples = []
    for idx, qid in enumerate(qids):
        for w_idx in range(3):  # annotation score idx
            y_true = qid2gt_scores_binary[qid][:, w_idx]
            y_predict = np.array(qid2pred_scores[qid])
            input_tuples.append((idx, w_idx, y_true, y_predict))

    if num_workers > 1:
        with mp.Pool(num_workers) as pool:
            for idx, w_idx, score in pool.imap_unordered(
                    compute_ap_from_tuple, input_tuples, chunksize=chunksize):
                ap_scores[idx, w_idx] = score
    else:
        for input_tuple in input_tuples:
            idx, w_idx, score = compute_ap_from_tuple(input_tuple)
            ap_scores[idx, w_idx] = score

    # it's the same if we first average across different annotations, then average across queries
    # since all queries have the same #annotations.
    mean_ap = float(f"{100 * np.mean(ap_scores):.2f}")
    return mean_ap


def compute_ap_from_tuple(input_tuple):
    idx, w_idx, y_true, y_predict = input_tuple
    if len(y_true) < len(y_predict):
        # print(f"len(y_true) < len(y_predict) {len(y_true), len(y_predict)}")
        y_predict = y_predict[:len(y_true)]
    elif len(y_true) > len(y_predict):
        # print(f"len(y_true) > len(y_predict) {len(y_true), len(y_predict)}")
        _y_predict = np.zeros(len(y_true))
        _y_predict[:len(y_predict)] = y_predict
        y_predict = _y_predict

    score = get_ap(y_true, y_predict)
    return idx, w_idx, score


def mk_gt_scores(gt_data, clip_length=2):
    """gt_data, dict, """
    num_clips = int(gt_data["duration"] / clip_length)
    saliency_scores_full_video = np.zeros((num_clips, 3))
    relevant_clip_ids = np.array(gt_data["relevant_clip_ids"])  # (#relevant_clip_ids, )
    saliency_scores_relevant_clips = np.array(gt_data["saliency_scores"])  # (#relevant_clip_ids, 3)
    saliency_scores_full_video[relevant_clip_ids] = saliency_scores_relevant_clips
    return saliency_scores_full_video  # (#clips_in_video, 3)  the scores are in range [0, 4]


def eval_highlight(submission, ground_truth, verbose=True):
    """
    Args:
        submission:
        ground_truth:
        verbose:
    """
    qid2preds = {d["qid"]: d for d in submission}
    qid2gt_scores_full_range = {d["qid"]: mk_gt_scores(d) for d in ground_truth}  # scores in range [0, 4]
    # gt_saliency_score_min: int, in [0, 1, 2, 3, 4]. The minimum score for a positive clip.
    gt_saliency_score_min_list = [2, 3, 4]
    saliency_score_names = ["Fair", "Good", "VeryGood"]
    highlight_det_metrics = {}
    for gt_saliency_score_min, score_name in zip(gt_saliency_score_min_list, saliency_score_names):
        start_time = time.time()
        qid2gt_scores_binary = {
            k: (v >= gt_saliency_score_min).astype(float)
            for k, v in qid2gt_scores_full_range.items()}  # scores in [0, 1]
        hit_at_one = compute_hl_hit1(qid2preds, qid2gt_scores_binary)
        mean_ap = compute_hl_ap(qid2preds, qid2gt_scores_binary)
        highlight_det_metrics[f"HL-min-{score_name}"] = {"HL-mAP": mean_ap, "HL-Hit1": hit_at_one}
        if verbose:
            print(f"Calculating highlight scores with min score {gt_saliency_score_min} ({score_name})")
            print(f"Time cost {time.time() - start_time:.2f} seconds")
    return highlight_det_metrics


# Use the count of each index, choose the highest as the mapping track_id index
def filter_submission_by_count(submission, ground_truth, id_mapping_path, verbose=True):
    """
    Filter submission based on ground_truth and id_mapping.jsonl.
    """
    id_mapping = {}
    with open(id_mapping_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            id_mapping[item["seq"]] = item

    submission_updated = []

    for gt in ground_truth:
        query = gt["query"].lower().replace(" ", "-")
        vid = gt["vid"].split("_")[0]
        seq_gt = f"{vid}+{query}"

        if seq_gt not in id_mapping:
            if verbose:
                print(
                    f"Warning: {seq_gt} not found in id_mapping.jsonl, no matching results between gt and prediction.")
            continue

        id_info = id_mapping[seq_gt]
        unique_gt_ids = id_info["unique_gt_ids"]
        unique_tracker_ids = id_info["unique_tracker_ids"]
        alpha_match_rows_list = id_info["alpha_match_rows_list"]
        alpha_match_cols_list = id_info["alpha_match_cols_list"]
        gt_ids_t_list = id_info["gt_ids_t_list"]
        tracker_ids_t_list = id_info["tracker_ids_t_list"]
        alpha_row_col_matches = id_info["alpha_row_col_matches"]

        track_id = gt["track_id"]

        # Step 1: Find the index of track_id in unique_gt_ids
        if track_id not in unique_gt_ids:
            if verbose:
                # GT does not have box information for this track_id in its time range
                print(f"Warning: track_id {track_id} not found in gt for seq {seq_gt}. unique_gt_ids: {unique_gt_ids}")
            continue
        idx_gt = unique_gt_ids.index(track_id)

        # Step 2: Traverse gt_ids_t_list and find the item containing idx_gt
        gt_ids_t_list_of_idx_gt = []
        for t, gt_ids_t in gt_ids_t_list:
            if idx_gt in gt_ids_t:
                gt_ids_t_list_of_idx_gt.append((t, gt_ids_t))

        # Step 3: Reverse key lookup
        keys = set()
        for t, gt_ids_t in gt_ids_t_list_of_idx_gt:
            for k, v in enumerate(gt_ids_t):
                if v == idx_gt:
                    keys.add(k)

        if len(keys) == 0:
            if verbose:
                print(
                    f"Warning: no matching key found for seq {seq_gt}, skipping this item. gt_ids_t_list_of_idx_gt: {gt_ids_t_list_of_idx_gt}")
            continue
        elif len(keys) != 1:
            if verbose:
                print(f"Warning: keys length != 1 for seq {seq_gt}, keys = {keys}")
        key = next(iter(keys))

        # Step 4: Filter alpha_match_rows_list according to gt_ids_t_list_of_idx_gt
        valid_ts = [t for t, _ in gt_ids_t_list_of_idx_gt]
        alpha_match_rows_list_gt = []
        for t, row_ids in alpha_match_rows_list:
            if t in valid_ts and key in row_ids:
                alpha_match_rows_list_gt.append((t, row_ids))

        # Step 5: Select the item in alpha_match_cols_list that corresponds to alpha_match_rows_list_gt
        alpha_match_cols_list_gt = []
        for t, cols in alpha_match_cols_list:
            if any(t == t_gt for t_gt, _ in alpha_match_rows_list_gt):
                alpha_match_cols_list_gt.append((t, cols))

        if not alpha_match_cols_list_gt:
            if verbose:
                print(f"Warning: No alpha_match_cols_list entry matched for seq {seq_gt}")
            continue

        # Step 6: According to alpha_match_cols_list_gt, count the number of times tracker_id appears
        tracker_id_counter = dict()
        for t, col_indices in alpha_match_cols_list_gt:
            tracker_ids_t = None
            for t_tracker, tracker_ids in tracker_ids_t_list:
                if t_tracker == t:
                    tracker_ids_t = tracker_ids
                    break
            if tracker_ids_t is None:
                continue

            for idx in col_indices:
                if idx < len(tracker_ids_t):
                    tracker_id = tracker_ids_t[idx]
                    if tracker_id not in tracker_id_counter:
                        tracker_id_counter[tracker_id] = 1
                    else:
                        tracker_id_counter[tracker_id] += 1

        if not tracker_id_counter:
            if verbose:
                print(f"Warning: No tracker_id matched for seq {seq_gt}")
            continue

        # Step 7: Get value with the highest count
        best_tracker_idx = max(tracker_id_counter.items(), key=lambda x: x[1])[0]

        if best_tracker_idx >= len(unique_tracker_ids):
            if verbose:
                print(
                    f"Error: tracker_idx {best_tracker_idx} out of bounds for unique_tracker_ids (len={len(unique_tracker_ids)}) for seq {seq_gt}")
            continue

        tracker_id = unique_tracker_ids[best_tracker_idx]

        # Step 9: Find a matching item in submission based on seq and tracker_id
        matched = None
        for s in submission:
            s_query = s["query"].lower().replace(" ", "-")
            s_vid = s["vid"].split("_")[0]
            s_seq = f"{s_vid}+{s_query}"

            if s_seq == seq_gt and s["track_id"] == tracker_id:
                matched = s
                break

        if matched:
            submission_updated.append(matched)
        else:
            if verbose:
                print(f"Warning: No matching submission found for seq {seq_gt} with tracker_id {tracker_id}")

    return submission_updated


def eval_submission(args, submission, ground_truth, verbose=True, match_number=False):
    """
    Args:
        submission: list(dict), each dict is {
            qid: str,
            query: str,
            vid: str,
            track_id: str,
            pred_relevant_windows: list([st, ed]),
            pred_saliency_scores: list(float), len == #clips in video.
                i.e., each clip in the video will have a saliency score.
        }
        ground_truth: list(dict), each dict is     {
          "qid": 7803,
          "query": "Man in gray top walks from outside to inside.",
          "duration": 150,
          "vid": "RoripwjYFp8_360.0_510.0",
          "track_id": 1,
          "relevant_windows": [[26, 46]],
          "relevant_clip_ids": [13, 14, 15, 16, 17]
          "saliency_scores": [[4, 4, 2], [3, 4, 2], [2, 2, 3], [2, 2, 2], [0, 1, 3]]
               each sublist corresponds to one clip in relevant_clip_ids.
               The 3 elements in the sublist are scores from 3 different workers. The
               scores are in [0, 1, 2, 3, 4], meaning [Very Bad, ..., Good, Very Good]
        }
        verbose:
        match_number:

    Returns:

    """
    pred_qids = set([e["qid"] for e in submission])
    gt_qids = set([e["qid"] for e in ground_truth])
    if match_number:
        assert pred_qids == gt_qids, \
            f"qids in ground_truth and submission must match. " \
            f"use `match_number=False` if you wish to disable this check"
    else:  # only leave the items that exists in both submission and ground_truth
        shared_qids = pred_qids.intersection(gt_qids)
        submission = [e for e in submission if e["qid"] in shared_qids]
        ground_truth = [e for e in ground_truth if e["qid"] in shared_qids]
    first_matching_ground_truth_length = len(ground_truth)
    first_matching_submission_length = len(submission)
    print(
        f"First matching is done! {first_matching_ground_truth_length} ground truth entries have been saved. {first_matching_submission_length} submissions have been saved")
    submission = filter_submission_by_count(submission, ground_truth, id_mapping_path=args.id_mapping_path,
                                            verbose=False)
    print(
        f"ID matching is done! {len(ground_truth)} ground truth entries have been saved. {len(submission)} submissions have been saved")

    # match again between ground truth and submission_filtered
    pred_qids = set([e["qid"] for e in submission])
    gt_qids = set([e["qid"] for e in ground_truth])
    if match_number:
        assert pred_qids == gt_qids, \
            f"qids in ground_truth and submission must match. " \
            f"use `match_number=False` if you wish to disable this check"
    else:  # only leave the items that exists in both submission and ground_truth
        shared_qids = pred_qids.intersection(gt_qids)
        submission = [e for e in submission if e["qid"] in shared_qids]
        ground_truth = [e for e in ground_truth if e["qid"] in shared_qids]
    second_matching_ground_truth_length = len(ground_truth)
    second_matching_submission_length = len(submission)
    print(
        f"Second matching is done! {second_matching_ground_truth_length} ground truth entries have been saved. {second_matching_submission_length} submissions have been saved")
    print(
        f"In the end, {second_matching_ground_truth_length} / {first_matching_ground_truth_length} = {second_matching_ground_truth_length / first_matching_ground_truth_length:.2%} ground truth entries have been saved. "
        f"{second_matching_submission_length} / {first_matching_submission_length} = {second_matching_submission_length / first_matching_submission_length:.2%} submissions have been saved")

    eval_metrics = {}
    eval_metrics_brief = OrderedDict()
    if "pred_relevant_windows" in submission[0]:
        moment_ret_scores = eval_moment_retrieval(
            submission, ground_truth, verbose=verbose)
        eval_metrics.update(moment_ret_scores)
        moment_ret_scores_brief = {
            "MR-full-mAP": moment_ret_scores["full"]["MR-mAP"]["average"],
            "MR-full-mAP@0.1": moment_ret_scores["full"]["MR-mAP"]["0.1"],
            "MR-full-mAP@0.3": moment_ret_scores["full"]["MR-mAP"]["0.3"],
            "MR-full-mAP@0.5": moment_ret_scores["full"]["MR-mAP"]["0.5"],
            "MR-full-mAP@0.7": moment_ret_scores["full"]["MR-mAP"]["0.7"],
            "MR-full-mIoU": moment_ret_scores["full"]["MR-mIoU"],
            "MR-full-R1@0.1": moment_ret_scores["full"]["MR-R1"]["0.1"],
            "MR-full-R1@0.3": moment_ret_scores["full"]["MR-R1"]["0.3"],
            "MR-full-R1@0.5": moment_ret_scores["full"]["MR-R1"]["0.5"],
            "MR-full-R1@0.7": moment_ret_scores["full"]["MR-R1"]["0.7"],
            "MR-full-R5@0.1": moment_ret_scores["full"]["MR-R5"]["0.1"],
            "MR-full-R5@0.3": moment_ret_scores["full"]["MR-R5"]["0.3"],
            "MR-full-R5@0.5": moment_ret_scores["full"]["MR-R5"]["0.5"],
            "MR-full-R5@0.7": moment_ret_scores["full"]["MR-R5"]["0.7"],
            "MR-full-R10@0.1": moment_ret_scores["full"]["MR-R10"]["0.1"],
            "MR-full-R10@0.3": moment_ret_scores["full"]["MR-R10"]["0.3"],
            "MR-full-R10@0.5": moment_ret_scores["full"]["MR-R10"]["0.5"],
            "MR-full-R10@0.7": moment_ret_scores["full"]["MR-R10"]["0.7"],
        }
        eval_metrics_brief.update(
            sorted([(k, v) for k, v in moment_ret_scores_brief.items()], key=lambda x: x[0]))

    if "pred_saliency_scores" in submission[0]:
        print(f'submission[0]: {submission[0]}')
        highlight_det_scores = eval_highlight(
            submission, ground_truth, verbose=verbose)
        eval_metrics.update(highlight_det_scores)
        highlight_det_scores_brief = dict([
            (f"{k}-{sub_k.split('-')[1]}", v[sub_k])
            for k, v in highlight_det_scores.items() for sub_k in v])
        eval_metrics_brief.update(highlight_det_scores_brief)

    # sort by keys
    final_eval_metrics = OrderedDict()
    final_eval_metrics["brief"] = eval_metrics_brief
    final_eval_metrics.update(sorted([(k, v) for k, v in eval_metrics.items()], key=lambda x: x[0]))
    return final_eval_metrics


def eval_main():
    import argparse
    parser = argparse.ArgumentParser(description="Moments and Highlights Evaluation Script")
    parser.add_argument("--submission_path", type=str, help="path to generated prediction file")
    parser.add_argument("--gt_path", type=str, help="path to GT file")
    parser.add_argument("--save_path", type=str, help="path to save the results")
    parser.add_argument("--not_verbose", action="store_true")
    parser.add_argument("--id_mapping_path", type=str, default='../results/id_mapping.jsonl',
                        help="path to id mapping file generated from MOT gt-prediction id matching, equals to SAVE_PATH defined in trackeval/eval")
    args = parser.parse_args()

    verbose = not args.not_verbose
    submission = load_jsonl(args.submission_path)
    gt = load_jsonl(args.gt_path)
    results = eval_submission(args, submission, gt, verbose=verbose)
    if verbose:
        print(json.dumps(results, indent=4))

    with open(args.save_path, "w") as f:
        f.write(json.dumps(results, indent=4))


if __name__ == '__main__':
    eval_main()
