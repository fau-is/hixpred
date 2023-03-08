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

To conduct our experiments, we used a publicly available dataset: https://data.4tu.nl/articles/dataset/Sepsis_Cases_-_Event_Log/12707639
As a predition target, we considered the Admission to IC which constitutes a possible outcome of a patient’s pathway, indicating whether a patient is required to transfer to the IC unit. Overall the dataset contains 995 instances with 98 positive labels.

Table 1: Times for training and testing (in seconds).
|               | Helpdesk |        |        |        |  Bpi2019 |         |         |         |
|---------------|:--------:|--------|--------|--------|:--------:|---------|---------|---------|
| Experiment    | Baseline | k=5    | k=10   | k=15   | Baseline | k=5     | k=10    | k=15    |
| Training time | 132.10   | 125.02 | 125.06 | 100.07 | 355.66   | 757.17  | 743.00  | 750.10  |
| Testing time  | 310.20   | 905.43 | 904.26 | 976.88 | 3609.98  | 6829.20 | 4652.48 | 5861.92 |
