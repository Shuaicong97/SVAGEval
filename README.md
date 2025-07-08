# SVAG Evaluation Toolkit
This is the official evaluation code for Spatial-Temporal Video Action Grounding (SVAG) task.
## Task definition
Given a video and a natural language query, our task requires detecting and tracking all referents that satisfy the query, along with their corresponding most relevant moments.

## Evaluation
The SVAG evaluation protocol consists of two complementary components: Spatial and Temporal evaluation, designed to assess both spatial accuracy and temporal consistency of visual grounding models.
### Spatial evaluation
Based on the [TrackEval](https://github.com/JonathonLuiten/TrackEval) repository.

We use [HOTA](TrackEval/Readme.md) as the evaluation metric.
### Temporal evaluation
Based on the `standalone_eval` from [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG) repository.

We use [mIoU, R1@X, R5@X, R10@X](temporal_eval/README.md) as the evaluation metrics.

Furthermore, we introduce **m-HIoU** as the metric to rank submissions on the competition server.
It is the average of HOTA and mIoU.
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

## Running the code
When ground truth for the test sets is known, the code can be run with one of the following commands:
```
cd scripts 
sh run.sh
```
```
cd scripts 
python run.py
```
Ensure the paths and filenames are correctly specified in `run.sh` or `run.py`.
The final evaluation output will be written into `combined_result_mean.json`, as defined by `OUTPUT_FILE` in `run.sh`
or by `final_result` in `run.py`.

## Format
The **ground truth** file is in JSON format. It should contain the following contents:
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
    "temporal": [[start,end]]
}
```
The **prediction** file is in JSON format. It should contain the following contents:
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

It must combine all three subsets (OVIS, MOT17 and MOT20).
Below is a concrete example of prediction:
```
{
    "datasets": [{
        "name": "OVIS",
        "queries": [{
            "query_id": 5113,
            "query": "The giraffe bends its neck around another giraffe",
            "video_id": 3,
            "video_name": "fb4a7958",
            "video_length": 79,
            "tracks": [{
                "track_id": 881,
                "spatial": [
                    null,[667.5802612304688,582.8107299804688,753.3036499023438,308.951904296875],
                    [645.5720825195312,582.27880859375,729.5850219726562,310.3974609375],
                    [638.4644775390625,594.1441650390625,681.0743408203125,299.79638671875],
                    ...
                ],
                "temporal":[
                    [10.0,74.0,0.33719998598098755],
                    [8.0,50.0,0.32989999651908875],
                    [12.0,32.0,0.29510000348091125],
                    ...
                ]
            }, ...] 
        }, ...]
    }, ...]
}
```
| entry                      | description                                                                                                                                                                             |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                     | `string`, dataset name. Must be one of `OVIS`, `MOT17`, or `MOT20`                                                                                                                      |
| `track_id`                 | `int`, unique track id for each instance                                                                                                                                                |
| `spatial`                  | `list(list or null)`, bounding box information. The list length is the length of the video. The value is either a specific box `[x,y,width,height]` or `null` (no object in this frame) |
| `temporal` in ground truth | `list(list)`, temporal ground truth. Each sublist contains 2 elements, `[start,end]`                                                                                                    |    
| `temporal` in prediction   | `list(list or null)`, moment retrieval predictions. The value is either a specific moment prediction `[start,end,score]` or `null` (no moment retrieval predictions)                    |    


## Codabench submission
To evaluate the results, please upload the submission file to the competition server. The submission file should be named ```submission.json``` and formatted as instructed above.

## Evaluate on your own custom benchmark
If you would like to evaluate performance without access to the ground truth of the official test set, you can create a custom benchmark in two ways:
1. **Split the provided training set** into a new training and held-out test/validation subset. This allows you to estimate performance using known ground truth from the original data.
2. **Use your dataset**, independent of the provided data. As long as your data is converted into the required ground truth and prediction formats, you can reuse the existing evaluation pipeline. See [Format](#format) for more details on the required format.



## License

SVAGEval is released under the [MIT License](LICENSE).

## Contact
If you encounter any problems with the code, feel free to post an issue. Please contact Shuaicong Wu ([niklaus.fangtasia@gmail.com](mailto:niklaus.fangtasia@gmail.com)) or [Tanveer Hannan](https://www.dbs.ifi.lmu.de/cms/personen/mitarbeiter/hannan/) 
([hannan@dbs.ifi.lmu.de](mailto:hannan@dbs.ifi.lmu.de)). If anything is unclear or hard to use, please leave a comment either via email or as an issue. We would love to help.

## Acknowledgement
We refer to the repositories [TrackEval](https://github.com/JonathonLuiten/TrackEval) and [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG). Thanks for their wonderful works.