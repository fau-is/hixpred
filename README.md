#  Hybrid Interpretable and Explainable Predictions for Patient Pathways (HIXPred)
## Technique
This project contains the source code for a novel hybrid interpretable and explainable technique for patient pathway prediction.

## Paper
If you use the code or fragments of it, please cite our paper:

```
@inprocessings{weinzierl2020nba,
    title={Precriptive Business Process Monitoring for Recommending Next Best Actions},
    author={Weinzierl, Sven and Dunzer, Sebastian and Zilker, Sandra and Matzner, Martin},
    booktitle={Proceedings of the 18th International Conference on Business Process Management Forum},
    year={2020},
    publisher={Springer}
}
```

## Data Set Characteristics

We conducted all experiments on a workstation with 12 CPUs, 128 GB RAM.
In Table 1, we present the times for training and testing of the baseline and our prescriptive business process monitoring technique.

Table 1: Times for training and testing (in seconds).
|               | Helpdesk |        |        |        |  Bpi2019 |         |         |         |
|---------------|:--------:|--------|--------|--------|:--------:|---------|---------|---------|
| Experiment    | Baseline | k=5    | k=10   | k=15   | Baseline | k=5     | k=10    | k=15    |
| Training time | 132.10   | 125.02 | 125.06 | 100.07 | 355.66   | 757.17  | 743.00  | 750.10  |
| Testing time  | 310.20   | 905.43 | 904.26 | 976.88 | 3609.98  | 6829.20 | 4652.48 | 5861.92 |
