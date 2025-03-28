import argparse
from convert_submission import generate_gt_txt, generate_predict_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SVAG Evaluation Script")

    parser.add_argument('--input_file', type=str, default='../data/mock_submission.json', help='submission json file')
    parser.add_argument('--eval_dir', type=str, default='../results/evaluation', help='path to the evaluation result')
    parser.add_argument('--convert_results_in_spatial_dir', type=str, default='../results/spatial',
                        help="Path to the spatial predictions")
    parser.add_argument('--convert_results_in_temporal_dir', type=str, default='../results/temporal',
                        help="Path to the temporal predictions")

    args = parser.parse_args()


    # First, the uploaded file must be converted into a format that can be evaluated in both dimensions.
    # gt format in spatial, jsonl format in temporal
    generate_gt_txt(args.input_file, args.convert_results_in_spatial_dir)
    generate_predict_dict(args.input_file, args.convert_results_in_temporal_dir)