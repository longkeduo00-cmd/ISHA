# Datasets

This directory contains 16 processed snapshots for the ten alignment tasks.

| Dataset | Snapshots | Source-target pairs |
| --- | --- | --- |
| Email-Enron | 2000-Q3, 2000-Q4, 2001-Q1 | 2000-Q3 to 2000-Q4; 2000-Q4 to 2001-Q1 |
| Contact-High-School | 2013-12-02, 2013-12-03, 2013-12-04 | 2013-12-02 to 2013-12-03; 2013-12-03 to 2013-12-04 |
| NDC-Classes | 2015, 2016, 2017 | 2015 to 2016; 2016 to 2017 |
| Tags-Ask-Ubuntu | B000, B001, B002 | B000 to B001; B001 to B002 |
| Congress-Bills | B000, B001, B002, B003 | B000 to B001; B002 to B003 |

`YYYY-Qk` denotes a calendar quarter, `YYYY-MM-DD` a date, `YYYY` a year, and `Bxxx` an event-order bin.

## Files

- Each snapshot text file contains one hyperedge per line, represented by integer node IDs.
- `manifest.json` lists file hashes, node counts and hyperedge counts.
- `seed_pool_manifest.json` lists the seed-hyperedge pools for the ten tasks.
- `../experiments/pairs_10_real.csv` specifies the source and target snapshot paths.

Shared node IDs define the ground truth. Identical hyperedges contain the same node set in both snapshots.

## Run the main experiment

From the repository root:

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

The output directory contains run-level precision, recall and F1 scores, their means and sample standard deviations, and the experiment settings.

Check the dataset files with:

```bash
python -m experiments.verify_datasets
```

## Sources

Original dataset descriptions and attribution:

- [Email-Enron](simplices/email-Enron/README.txt)
- [Contact-High-School](simplices/contact-high-school/README.txt)
- [NDC-Classes](simplices/NDC-classes/README.txt)
- [Tags-Ask-Ubuntu](simplices/tags-ask-ubuntu/README.txt)
- [Congress-Bills](simplices/congress-bills/README.txt)

Original data attribution and usage terms apply.
