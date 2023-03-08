#  Hybrid Interpretable and Explainable Predictions for Patient Pathways (HIXPred)
## Technique
This project contains the source code for a novel hybrid interpretable and explainable technique for patient pathway prediction.

## Paper
If you use the code or fragments of it, please cite our paper:

```
@inprocessings{zilker2023hixpred,
    title={Best of Both Worlds: Combining Predictive Power with Interpretable and Explainable Results for Patient Pathway Prediction},
    author={Zilker, Sandra and Weinzierl, Sven and Zschech, Patrick and Kraus, Mathias and Matzner, Martin},
    booktitle={Proceedings of the 31st European Conference on Information Systems},
    year={2023},
    publisher={AIS}
}
```

## Data Set Characteristics

To conduct our experiments, we used a publicly available dataset: https://data.4tu.nl/articles/dataset/Sepsis_Cases_-_Event_Log/12707639.
As a predition target, we considered the Admission to IC which constitutes a possible outcome of a patient’s pathway, indicating whether a patient is required to transfer to the IC unit. Overall the dataset contains 995 instances with 98 positive labels. 

The data set contains static and sequential features. The static features are all categorical, e.g., the activity.
Characteristics of the four sequential features can be found in the table below.

Table 1: Characteristics of sequential features.

|                                                             | Percentile                                  |
                                                              |:--------------------------------------------:|
|               | Observations  | Mean   | Standard Deviation | 25%      |  50%     |  75%      | 95%       | 
|---------------|:------------: |:------:|:------------------:|:--------:|:--------:|:---------:|:---------:|
| Age           | 724           | 72.12  |15.48               |65.0      | 75.0     | 85.0      |  90.0     | 
| CRP           | 2,388         | 111.66 |83.53               | 44.0     | 94.0     | 156.0     | 276.0     |
| Leucocytes    | 2,525         | 13.24  |16.87               | 7.6      | 11.0     | 15.1      | 24.9      |
| Lactic Acis   | 992           | 1.98   |1.49                |1.1       | 1.6      |2.3        |4.7        |
