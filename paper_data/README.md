# Paper data

This directory contains the run-level results, summary tables and figure-source data for the ISHA experiments.

## Files

| Path | Contents |
| --- | --- |
| `main_accuracy/runs.csv` | Precision, recall, F1 score and matching counts for 7,500 runs |
| `main_accuracy/summary.csv` | Mean and sample standard deviation for each method, pair and seed-hyperedge ratio |
| `ablation/runs.csv` | Results for ISHA and ISHA without iteration on Congress-Bills and NDC-Classes |
| `ablation/run_level_pair_means.csv` | The two source-target pairs averaged within each repetition |
| `ablation/figure_source_data.csv` | Means and sample standard deviations used in the ablation figure |
| `efficiency/runs.csv` | Accuracy, runtime and peak memory for 400 runs on Tags-Stack-Overflow and Threads-Ask-Ubuntu |
| `efficiency/accuracy_summary.csv` | Mean and sample standard deviation of the efficiency-experiment accuracy scores |
| `efficiency/figure_source_data.csv` | Median runtime and memory, with first and third quartiles |
| `efficiency/input_statistics.csv` | Input statistics for the ten efficiency hypergraph pairs |
| `tables/alignment_dataset_statistics.csv` | Statistics of the ten alignment tasks |
| `tables/efficiency_full_dataset_statistics.csv` | Statistics of the two full datasets used for efficiency experiments |
| `tables/manuscript_f1_targets.csv` | F1 means and sample standard deviations reported in the paper |
| `verification.json` | Numeric verification results and source-file hashes |
| `file_manifest.json` | Hashes of the files in this directory |
| `verify_results.py` | Script for checking the result files |

## Statistics

- Main accuracy: ten source-target pairs, three seed-hyperedge ratios, five methods and 50 repetitions.
- Ablation: Congress-Bills and NDC-Classes, two source-target pairs per dataset, ten seed-hyperedge ratios, two variants and 50 repetitions.
- Efficiency: Tags-Stack-Overflow and Threads-Ask-Ubuntu, five node scales, four methods and ten repetitions.
- Precision is `correct_matches / predicted_matches`; recall is `correct_matches / ground_truth_total`; F1 score is `2 * correct_matches / (predicted_matches + ground_truth_total)`.
- Main and efficiency accuracy summaries use the mean and sample standard deviation of run-level scores.
- Ablation curves first average the two source-target pairs in each repetition, then calculate the mean and sample standard deviation across 50 repetitions.
- Runtime is in seconds. Peak memory is in MiB. Efficiency curves use the median, with the first and third quartiles as error bars.

## Full-dataset statistics

| Dataset | Nodes | Events | Distinct hyperedges |
| --- | ---: | ---: | ---: |
| Tags-Stack-Overflow | 49,998 | 14,458,875 | 5,537,637 |
| Threads-Ask-Ubuntu | 125,602 | 192,947 | 166,999 |

Distinct hyperedges are unique node sets.

## Check the results

From the repository root:

```bash
python paper_data/verify_results.py
```

The script checks run-level metrics, summary statistics, figure-source values, dataset statistics and file hashes. F1 means and sample standard deviations are compared with the paper at three decimal places.

## Run experiments

Commands for the main experiment and iteration ablation are in the [main README](../README.md#main-experiment).
