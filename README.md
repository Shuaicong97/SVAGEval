# SVAG Evaluation Toolkit
This is the official evaluation code for Spatial-Temporal Video Action Grounding (SVAG) task.
## Task Definition
Given a video and a natural language query, our task requires detecting and tracking all referents that satisfy the query, along with their corresponding most relevant moments.

## Evaluation
The SVAG evaluation protocol consists of two complementary components: Spatial and Temporal evaluation, designed to assess both spatial accuracy and temporal consistency of visual grounding models.
### Spatial Evaluation
Based on the [TrackEval](https://github.com/JonathonLuiten/TrackEval) repository.

We use [HOTA](TrackEval/Readme.md) as the evaluation metric.
### Temporal Evaluation
Based on the `standalone_eval` from [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG) repository.

We use [R1@X, R5@X, R10@X, mAP, mIoU](temporal_eval/README.md) as the evaluation metrics.
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

## Run
Basic usage.
```
cd scripts 
sh run.sh
```
The final evaluation output will be written into `combined_result_mean.json`, as defined by `OUTPUT_FILE` in the `run.sh`.

## Format
The prediction file is in JSON format. It should contain the following contents:
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

It must combine all three subsets (OVIS, MOT17 and MOT20). The `name` in `dataset` must be one of `OVIS`, `MOT17`, or `MOT20`.
Below is a concrete example:
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


## Codabench Submission
To evaluate the results, please upload the submission file to the competition server. The submission file should be named ```submission.json``` and formatted as instructed above.

## License

SVAGEval is released under the [MIT License](LICENSE).

## Contact
If you encounter any problems with the code, feel free to post an issue. Please contact [Tanveer Hannan](https://www.dbs.ifi.lmu.de/cms/personen/mitarbeiter/hannan/) 
([hannan@dbs.ifi.lmu.de](mailto:hannan@dbs.ifi.lmu.de)). If anything is unclear or hard to use, please leave a comment either via email or as an issue. We would love to help.

## Acknowledgement
We refer to the repositories [TrackEval](https://github.com/JonathonLuiten/TrackEval) and [FlashVTG](https://github.com/Zhuo-Cao/FlashVTG). Thanks for their wonderful works.