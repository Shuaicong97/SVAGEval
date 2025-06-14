# Temporal Evaluation

## Metrics explanation

*[FlashVTG: Feature Layering and Adaptive Score Handling Network for Video Temporal Grounding](https://arxiv.org/pdf/2412.13441?). WACV 2025. Cao, Zhuo and Zhang, Bingqing and Du, Heming and Yu, Xin and Li, Xue and Wang, Sen.*

- R1@X: It stands for "Recall 1 at X", which refers to choosing the temporal segment prediction with the highest confidence score and checking whether its IoU with any ground truth moment exceeds the threshold X. 
- R5@X: Similar to R1@X, while choosing the top 5 predictions.
- R10@X: Similar to R1@X, while choosing the top 10 predictions.
- mAP: mean of the average precision (AP) across all queries at certain thresholds.
- mIoU: Measure the average overlap between the predicted and ground truth moments.