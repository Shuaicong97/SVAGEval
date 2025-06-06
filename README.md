# SVAG Evaluation Toolkit
This is the official evaluation code for Spatial-Temporal Video Action Grounding (SVAG) task.
## Evaluation
The SVAG evaluation protocol consists of two complementary components: Spatial and Temporal evaluation, designed to assess both spatial accuracy and temporal consistency of visual grounding models.
### Spatial Evaluation
Based on the [TrackEval](https://github.com/JonathonLuiten/TrackEval) repository.

We use HOTA as the evaluation metric.
### Temporal Evaluation
Based on the `standalone_eval` from [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG) repository.

We use R1@X, R5@X, R10@X, mAP, mIoU as the evaluation metrics.
## Preparation
Clone this repository.
```
git clone https://github.com/Shuaicong97/SVAGEval.git
cd SVAGEval
```
Download the packages. Python version 3.10.16 can be used for reproduce.
```
pip install -r requirements.txt
```
Prepare the submission file in the specified format.
```
{
    "datasets": [dataset]
}

dataset{
    "name": string,
    "queries": [query]
}

query{
	"query_id": int,
	"query": string
	"video_id": int,
	"video_name": string,
	"video_length": int,
	"tracks": [track]
}

track{
	"track_id": int,
  	"spatial": [[x,y,width,height] or None],
  	"temporal": [[start,end,score] or None]
}
```
## Step 0 (Admin)
Convert ground_truth.json.
```
cd scripts 
python convert_valid_gt_all.py
```
## Running Evaluation
Basic usage.
```
cd scripts 
sh run.sh
```
To evaluate the results, please upload the submission file to the competition server.

## Output
The final evaluation output is a JSON file, combining the spatial and temporal evaluation results. The path is OUTPUT_FILE defined in the `run.sh`.
## Acknowledgement
We refer to the repositories [TrackEval](https://github.com/JonathonLuiten/TrackEval) and [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG). Thanks for their wonderful works.