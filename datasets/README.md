# Dataset snapshots

These are the exact processed hypergraph snapshots used in the ten alignment tasks and the 1,500-run reproduction check. The 16 snapshot files total 1,732,125 bytes. Their contents, node IDs, hyperedge order, and line endings are preserved from the supplied server archive `1013.tar.gz`.

| Dataset | Included snapshots | Source-target tasks |
| --- | --- | --- |
| Email-Enron | 2000-Q3, 2000-Q4, 2001-Q1 | 2000-Q3 to 2000-Q4; 2000-Q4 to 2001-Q1 |
| Contact-High-School | 2013-12-02, 2013-12-03, 2013-12-04 | 2013-12-02 to 2013-12-03; 2013-12-03 to 2013-12-04 |
| NDC-Classes | 2015, 2016, 2017 | 2015 to 2016; 2016 to 2017 |
| Tags-Ask-Ubuntu | B000, B001, B002 | B000 to B001; B001 to B002 |
| Congress-Bills | B000, B001, B002, B003 | B000 to B001; B002 to B003 |

`YYYY-Qk` identifies a calendar quarter, `YYYY-MM-DD` a calendar date, and `YYYY` a calendar year. `Bxxx` identifies an event-order bin, not a calendar period. The source archive's preprocessing settings determine the bin boundaries; the bundled files are already partitioned and must not be repartitioned to reproduce the reported experiments.

## Format and evaluation

Each nonempty line contains the integer node IDs of one hyperedge. Keep the files unchanged for reproduction. Shared node IDs define the ground-truth correspondences for these labeled snapshots. An identical hyperedge has the same node set in both snapshots; the experiment runner samples seed hyperedge pairs from this pool.

Ground-truth node identities are used to evaluate predictions, not provided as node seeds to ISHA. Nodes covered by seed hyperedges still need to be aligned and remain in the evaluation.

## Verification and reproduction

From the repository root:

```bash
python -m experiments.verify_datasets
python -m experiments.run_pairs --pairs experiments/pairs_10_real.csv --data-root . --seed-pool-manifest datasets/seed_pool_manifest.json --alpha-values 0.1,0.4,0.7 --repeats 50 --max-rounds 10 --identity-ground-truth --output-dir outputs/paper_50
```

`manifest.json` records the SHA256, byte count, node count, and hyperedge count of every snapshot. `seed_pool_manifest.json` preserves the ordered seed-hyperedge pools used during verification. Its fingerprints were checked against all 1,500 corresponding archived server trials. Using this file avoids changes to seed sampling caused by reconstructing an unordered pool in another environment.

The experiment writes true run indices and random seeds, precision, recall, F1 score, and matching counts. Its summaries use the mean and sample standard deviation over 50 runs. It never overwrites an existing output directory.

## Source documentation

The supplied source-data README files are retained unchanged:

- [Email-Enron](simplices/email-Enron/README.txt)
- [Contact-High-School](simplices/contact-high-school/README.txt)
- [NDC-Classes](simplices/NDC-classes/README.txt)
- [Tags-Ask-Ubuntu](simplices/tags-ask-ubuntu/README.txt)
- [Congress-Bills](simplices/congress-bills/README.txt)

These source README files describe the original collections and may mention raw files or preprocessing scripts that are not bundled here. This directory contains processed snapshots, not the complete raw collections, personal label lookup files, or experiment results. Original data attribution and usage terms remain applicable. No new licence is granted for these snapshots.
