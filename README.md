# ISHA

**Iterative Seed-guided Hypergraph Alignment** identifies node correspondences between two hypergraphs from a small set of corresponding hyperedges. The node mappings inside each seed hyperedge pair are unknown.

## Method

1. Initialize a sparse node-pair similarity matrix from the seed hyperedges.
2. Score each unmatched candidate using `T[i,j] / (K1[i] + K2[j])`, where `K1` and `K2` are node hyperdegrees.
3. Accept node pairs that are mutually highest-scoring candidates.
4. Use the newly matched pairs to update similarities through their incident hyperedges.
5. Repeat matching and propagation until no new pair is accepted or the maximum number of rounds is reached.

The default maximum is ten rounds. Setting `--max-rounds 1` runs ISHA without iteration.

## Installation

Requirements: Python 3.12, NumPy and SciPy. ISHA runs on a CPU.

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

Install the dependencies and package:

```bash
python -m pip install -r requirements.txt
python -m pip install --no-deps -e .
```

## Quick start

```bash
python -m isha --source examples/source.txt --target examples/target.txt --seeds examples/seed_hyperedges.csv --ground-truth examples/ground_truth.csv --output outputs/demo.csv
```

The command saves the predicted node pairs to `outputs/demo.csv` and prints precision, recall and F1 score. The ground-truth file is used for evaluation.

## Input files

### Hypergraphs

Each nonempty line contains the nonnegative integer IDs of the nodes in one hyperedge:

```text
0 1
1 2
```

### Seed hyperedge pairs

The seed CSV lists the zero-based hyperedge positions in the source and target files:

```csv
source_edge,target_edge
0,0
```

### Ground truth

The optional ground-truth CSV lists corresponding source and target nodes:

```csv
source,target
0,10
1,11
2,12
```

Omit `--ground-truth` to obtain predicted matches without calculating accuracy metrics.

## Main experiment

The ten source-target pairs are listed in `experiments/pairs_10_real.csv`. The corresponding snapshots are in `datasets/`.

Run ISHA at three seed-hyperedge ratios with 50 repetitions:

```bash
python -m experiments.run_pairs \
  --pairs experiments/pairs_10_real.csv \
  --data-root . \
  --seed-pool-manifest datasets/seed_pool_manifest.json \
  --alpha-values 0.1,0.4,0.7 \
  --repeats 50 \
  --max-rounds 10 \
  --identity-ground-truth \
  --output-dir outputs/paper_50
```

`--identity-ground-truth` uses shared node IDs as the ground truth for these dataset snapshots. `datasets/seed_pool_manifest.json` specifies the seed-hyperedge pools. Repetition `r` uses random seed `42 + r`.

## Iteration ablation

Run the full method across ten seed-hyperedge ratios:

```bash
python -m experiments.run_pairs \
  --pairs experiments/pairs_10_real.csv \
  --data-root . \
  --seed-pool-manifest datasets/seed_pool_manifest.json \
  --alpha-values 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 \
  --repeats 50 \
  --max-rounds 10 \
  --identity-ground-truth \
  --output-dir outputs/ablation_full
```

Run the noniterative variant with the same seed settings:

```bash
python -m experiments.run_pairs \
  --pairs experiments/pairs_10_real.csv \
  --data-root . \
  --seed-pool-manifest datasets/seed_pool_manifest.json \
  --alpha-values 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 \
  --repeats 50 \
  --max-rounds 1 \
  --identity-ground-truth \
  --output-dir outputs/ablation_one_round
```

### Experiment outputs

Each output directory contains:

| File | Contents |
| --- | --- |
| `raw_results.csv` | Precision, recall, F1 score, matching counts, runtime and random seed for each run |
| `summary.csv` | Mean and sample standard deviation for each pair and seed-hyperedge ratio |
| `run_config.json` | Experiment parameters and software versions |
| `seed_pool_manifest.json` | Seed-hyperedge pools used by the experiment |

Use a new output directory for each experiment.

## Paper data

[paper_data/README.md](paper_data/README.md) describes the main-experiment results, ablation results, efficiency measurements and dataset statistics.

```bash
python paper_data/verify_results.py
```

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

## Repository layout

| Path | Contents |
| --- | --- |
| `isha/` | Core method, Python API, command-line interface and evaluation metrics |
| `experiments/run_pairs.py` | Repeated experiments on source-target hypergraph pairs |
| `experiments/pairs_10_real.csv` | The ten alignment tasks |
| `datasets/` | Processed snapshots and seed-hyperedge pools |
| `paper_data/` | Run-level results, summary tables and figure-source data |
| `examples/` | Small example inputs |
| `tests/` | Unit tests |

## Tests

```bash
python -m unittest discover -s tests -v
python -m experiments.verify_datasets
```

## License

No license has been selected for the method code. Dataset attribution and usage terms are provided in the source README files.
