# ISHA

**Iterative Seed-guided Hypergraph Alignment** aligns nodes between two hypergraphs using a small set of corresponding hyperedges. The node correspondences inside each seed hyperedge pair are unknown. ISHA does not require seed-node correspondences or neural-network training.

This repository contains the standalone ISHA method, a command-line interface, evaluation utilities, a repeated-experiment runner, small synthetic examples, the processed dataset snapshots used for the ten paper alignment tasks, and verified numeric evidence in [`paper_data/`](paper_data/README.md). 


## Method

1. Initialize sparse node-pair evidence from the seed hyperedge pairs. Each seed pair contributes one to every source-target node pair contained in those hyperedges.
2. Score unmatched candidates using `T[i,j] / (K1[i] + K2[j])`, where `T` is the accumulated evidence and `K1`, `K2` are node hyperdegrees.
3. Accept a candidate only when it is the highest-scoring candidate for both endpoints.
4. Use newly accepted node pairs to select related incident hyperedge pairs and add evidence to their remaining unmatched node pairs.
5. Stop when no new matches can be accepted or the maximum number of rounds is reached. The default is **10 rounds**; one round is the noniterative ablation.

Only positive-evidence candidates are considered. The server implementation's validity guard and floating-point operation order are retained. Equal candidate scores use stable source-node and sorted sparse-column order. Equal hyperedge-overlap scores prefer an equal hyperedge size, then a smaller target hyperedge, then more unmatched target nodes; remaining ties preserve the input hyperedge order. No rule rewards equal source and target node IDs.

## Installation

Use Python **3.12**. The pinned dependency versions are the environment used for the local reproduction check.

```bash
git clone https://github.com/longkeduo00-cmd/ISHA.git
cd ISHA
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
```

The method uses NumPy and SciPy on a CPU. A GPU is not required.

## Quick start

```bash
python -m isha --source examples/source.txt --target examples/target.txt --seeds examples/seed_hyperedges.csv --ground-truth examples/ground_truth.csv --output outputs/demo.csv
```

The example uses different node IDs in the two hypergraphs. Ground truth is used **only for evaluation**, not for alignment. Output files are not overwritten: choose a new output path when repeating the command.

For the noniterative variant, add `--max-rounds 1`.

## Input formats

### Hypergraphs

Each nonempty line is one hyperedge containing whitespace-separated, nonnegative integer node IDs:

```text
0 1
1 2
```

Duplicate hyperedges and input hyperedge order are preserved. Use reasonably compact node IDs: the sparse matrix dimensions depend on the largest ID. Source and target IDs need not be equal, but all IDs must be nonnegative integers.

### Seed hyperedge pairs

Provide a CSV containing **zero-based positions** in the source and target hyperedge files:

```csv
source_edge,target_edge
0,0
```

Only the hyperedge correspondence is supplied. Do not list internal node correspondences here.

### Ground truth (optional)

For labeled evaluation, provide a CSV with known source-target node pairs:

```csv
source,target
0,10
1,11
2,12
```

Without `--ground-truth`, the command outputs predicted matches but does not claim alignment accuracy.

## Python API

```python
from isha import align_hypergraphs, evaluate_alignment

source = [{0, 1}, {1, 2}]
target = [{10, 11}, {11, 12}]
seed_pairs = [(source[0], target[0])]

matches = align_hypergraphs(source, target, seed_pairs, max_rounds=10)
metrics = evaluate_alignment(matches, {0: 10, 1: 11, 2: 12})
print(matches)
print(metrics)
```

## Evaluation

Let `TP` be the number of correctly predicted node pairs, `P` the number of predicted pairs, and `G` the number of ground-truth pairs:

- Precision: `TP / P`.
- Recall: `TP / G`.
- F1 score: `2 * TP / (P + G)`.

Undefined ratios are reported as zero. Predictions and ground truth must each be one-to-one. Nodes covered by seed hyperedges remain in the evaluation: their internal mappings were not supplied to ISHA.

## Repeated experiments

For snapshots whose shared node IDs define the ground truth, prepare a CSV:

```csv
dataset,source,target
DatasetName,path/to/source.txt,path/to/target.txt
```

Then run:

```bash
python -m experiments.run_pairs --pairs pairs.csv --data-root . --alpha-values 0.1,0.4,0.7 --repeats 50 --max-rounds 10 --identity-ground-truth --output-dir outputs/run_50
```

The runner samples `max(1, floor(alpha * number_of_identical_hyperedges))` seed pairs. Run `r` uses random seed `42 + r`. It records the actual run index, seed, seed-hyperedge fingerprint, correct-match count, predicted-match count, ground-truth count, precision, recall, and F1 score. The summary uses the mean and **sample standard deviation** (`ddof=1`) across runs.

`--identity-ground-truth` explicitly confirms the labeled-snapshot evaluation assumption. It is not required for ordinary alignment with independently specified seed pairs.

The default `--seed-order server` preserves the legacy server seed-pool construction. `--seed-order sorted` gives a canonical order for new experiments, but changes the sampled seeds and should not be used to reproduce the legacy paper results. Every run saves `seed_pool_manifest.json`; reuse it with `--seed-pool-manifest` to freeze seed-pool order across environments. Keep the same input files, node labels, hyperedge order, dependency versions, and seed schedule when comparing results. Hardware speed alone does not determine alignment accuracy; software versions and tie order can affect reproducibility.

Example runner smoke test:

```bash
python -m experiments.run_pairs --pairs examples/pairs.csv --alpha-values 0.4 --repeats 2 --identity-ground-truth --output-dir outputs/toy_run
```

`experiments/pairs_10_real.csv` lists the ten paper snapshot pairs from Email-Enron, Contact-High-School, NDC-Classes, Tags-Ask-Ubuntu, and Congress-Bills. All 16 distinct snapshot files are included under `datasets/`; no separate data download is needed. From the repository root, first verify the files and then reproduce the 50-run experiments using the frozen seed-pool order:

```bash
python -m experiments.verify_datasets
python -m experiments.run_pairs --pairs experiments/pairs_10_real.csv --data-root . --seed-pool-manifest datasets/seed_pool_manifest.json --alpha-values 0.1,0.4,0.7 --repeats 50 --max-rounds 10 --identity-ground-truth --output-dir outputs/paper_50
```

See [datasets/README.md](datasets/README.md) for the included snapshots, data format, and provenance. The supplied source-data README files are retained with each dataset. Names, email addresses, node-label lookup files, and the complete unprocessed event collections are not included.

The runner is sequential, so its timing is not the original parallel efficiency benchmark. It is intended to reproduce alignment metrics, not to compare CPU runtime or peak memory against baselines.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover one-to-one matching, distinct source-target IDs, propagation beyond the seed hyperedges, the one-round ablation, mutual selection, input validation, and independently specified ground-truth metrics.

### Reproduction check

Before publication, both the supplied server implementation and this standalone core were run on all ten real source-target pairs, at seed-hyperedge ratios `0.1`, `0.4`, and `0.7`, with **50 repetitions per setting**. Each implementation completed 1,500 runs.

- All 1,500 predicted node mappings from the standalone core were identical to those from the server implementation.
- Precision, recall, and F1 score agreed with the corresponding archived server trials within `1e-12`.
- All 30 F1 means and sample standard deviations agreed with the supplied paper table to three decimal places.

This check used Python 3.12.10, NumPy 2.5.3, and SciPy 1.18.1 on Windows. It verifies these inputs and settings, not arbitrary software versions or different seed samples. The processed benchmark snapshots are included and match the checked input hashes. Archived numeric measurements are available in [`paper_data/`](paper_data/README.md); original local re-execution logs and full unprocessed datasets are not included.

## Repository layout

```text
isha/                 Core method, API, file I/O, metrics, and CLI
experiments/          Repeated labeled-snapshot evaluation
datasets/             Verified snapshots, checksums, and frozen seed-pool order
examples/             Small synthetic inputs
tests/                Unit tests
requirements.txt      Pinned reproduction environment
```

## License

No license has been selected for the method code. Inclusion of third-party dataset snapshots does not change their original ownership or usage terms; preserve their source attribution and check the original terms before redistribution.
