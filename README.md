# SVAG Evaluation Toolkit
This is the official evaluation code for Spatial-Temporal Video Action Grounding (SVAG) tasks.
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
Download the packages. Code can be run with only numpy, scipy and scikit-learn. Python version 3.7.16 can be used for reproduce.
```
pip install -r requirements.txt
```
Prepare the submission file in the specified format.
```
{
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
Generate the seqmap.txt files for all needed datasets.
## Running Evaluation
Basic usage.
```
cd scripts 
sh run_svag.sh
```
## Output
The final evaluation output is a JSON file, combining the spatial and temporal evaluation results. The path is COMBINED_RESULT_PATH defined in the `run_svag.sh`.
## Acknowledgement
We refer to the repositories [TrackEval](https://github.com/JonathonLuiten/TrackEval) and [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG). Thanks for their wonderful works.