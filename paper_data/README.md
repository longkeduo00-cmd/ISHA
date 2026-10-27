# Numeric evidence for the ISHA manuscript

This directory contains archived run-level measurements and recomputed source tables for the manuscript **Iterative seed-guided hypergraph alignment via consistency propagation**. It is not a new experiment run. The repository remains private, and no data licence or repository visibility has been changed.

## Coverage

| Manuscript item | Files | Coverage |
| --- | --- | --- |
| Table 2: alignment-task statistics | `tables/alignment_dataset_statistics.csv` | Ten source-target pairs; counts independently checked against the processed snapshots already in `datasets/` |
| Table 4: main alignment accuracy | `main_accuracy/runs.csv`, `main_accuracy/summary.csv` | Ten pairs, three seed-hyperedge ratios, five methods, 50 repetitions: 7,500 run records |
| Figure 2: iteration ablation | `ablation/runs.csv`, `ablation/run_level_pair_means.csv`, `ablation/figure_source_data.csv` | Congress-Bills and NDC-Classes, two pairs each, ten ratios, two variants, 50 repetitions: 4,000 run records |
| Table 5: efficiency-experiment accuracy | `efficiency/runs.csv`, `efficiency/accuracy_summary.csv` | Tags-Stack-Overflow and Threads-Ask-Ubuntu, five scales, four CPU methods, ten repetitions: 400 run records |
| Figure 3: runtime and memory | `efficiency/figure_source_data.csv` | Medians and first/third quartiles calculated from the same 400 efficiency records |
| Efficiency input sizes | `efficiency/input_statistics.csv` | Node, hyperedge, incidence and other aggregate counts for the ten evaluated input pairs |

The notation table and method diagram do not contain experimental measurements. Coauth-DBLP and Grad-Align+ efficiency results are outside the scope of the current manuscript's efficiency comparison and are not included in these files. The included efficiency settings all have ten successful records; no failed trial was removed from an included setting.

## Aggregation and definitions

- For each run, precision is `correct_matches / predicted_matches`; recall is `correct_matches / ground_truth_total`; F1 score is `2 * correct_matches / (predicted_matches + ground_truth_total)`. A zero denominator yields zero. `ground_truth_total` is the method-specific evaluation denominator recorded by the original experiment; it must not be replaced by one common denominator for all methods.
- Main-accuracy summaries are the arithmetic mean and **sample** standard deviation (`ddof=1`) of the 50 run-level scores in each pair-method-ratio setting. Mean F1 is not computed from the mean precision and mean recall.
- For the ablation, first average the two source-target pairs within each dataset, ratio, variant and repetition. The figure mean and sample standard deviation are then calculated over the 50 resulting values. These are not standard deviations between the two pair means.
- Efficiency accuracy uses the mean and sample standard deviation over ten runs. Runtime and peak process-tree resident memory use the median and the 25th/75th percentiles, with linear percentile interpolation. Runtime is in seconds; `peak_rss_mb` retains the archived unit (bytes divided by `1024**2`, i.e. MiB).
- Repetition seeds are `42 + run_idx` for the main and ablation experiments, and `42 + repeat` for efficiency. Seed fingerprints are included where recorded. The two ablation variants use the same seed-hyperedge sample in each paired comparison.

## Verification against the manuscript

`tables/manuscript_f1_targets.csv` transcribes only the 190 reported F1 mean/SD cells from the checked manuscript version. Its source manuscript's SHA256 is recorded in `verification.json`; the manuscript itself is not redistributed.

All 150 main-accuracy cells and all 40 efficiency-accuracy cells agree with the manuscript when rounded to three decimal places. Recomputed ablation and efficiency source tables agree with the existing figure-source CSVs to floating-point precision. All 600 overlapping full-ISHA trials in the main and reported ablation experiments agree in precision, recall and F1.

The original main summaries used a different standard-deviation convention in some historical files. This package recomputes sample standard deviations from the selected archived **trial-audit** records. It does not copy the historical summary SDs. The selected Tags-Ask-Ubuntu B000-B001 rerun is explicitly identified in `verification.json`, following the source selection documented during the original manuscript analysis.

### Known manuscript Table 3 discrepancy — not certified

The full-collection descriptive table is **excluded from the verified table exports**. For Tags-Stack-Overflow, a full scan of the supplied source data gives:

| Quantity | Count |
| --- | ---: |
| Nodes | 49,998 |
| Recorded events | 14,458,875 |
| Distinct ordered node sequences | 5,675,497 |
| Distinct hyperedges, treating each hyperedge as an unordered node set | 5,537,637 |

The checked manuscript reports 5,675,497 as the number of distinct hyperedges, while its caption defines distinct hyperedges as unique node sets. This is a definition/count discrepancy, not a rounding difference. The manuscript was not changed by this export. Threads-Ask-Ubuntu's unordered-set counts agree with the manuscript: 125,602 nodes, 192,947 events and 166,999 distinct hyperedges. Source hashes and the discrepancy are recorded in `verification.json`.

## Recheck locally

From the repository root, with Python 3.12:

```bash
python paper_data/verify_results.py
```

The verification script uses only the Python standard library. It independently recalculates metrics, means, sample standard deviations, pair averages, medians, quartiles, the rounded manuscript targets, and the ten alignment-pair statistics. `file_manifest.json` allows all released file bytes to be checked. The original source-collection files are not bundled, so the full-collection count scan is documented in the audit rather than rerun by this command.

## Provenance and exclusions

Sources are the user-supplied archives `928.tar.gz`, `928-ablation.tar.gz` and `930ef.tar.gz`, plus the already versioned processed alignment snapshots. Archive hashes and selected main-result member hashes are in `verification.json`.

Only numeric results, match counts, seeds, seed fingerprints, aggregate input counts and provenance are exported. Absolute server paths, logs, tracebacks, personal label lookups, node-level prediction lists, the full manuscript, and full raw source datasets are not added. No new experiment was run, no method parameter was tuned, and no historical weighting option was added back to the ISHA implementation.

Access to a private GitHub repository is not equivalent to anonymous reviewer access. The corresponding author must separately arrange the review access described in the manuscript's availability statements.
