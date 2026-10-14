import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import time
from pathlib import Path

import numpy as np
import scipy

from isha import align_hypergraphs, evaluate_alignment
from isha.io import load_hypergraph


def fingerprint(edges):
    canonical = [",".join(map(str, sorted(edge))) for edge in edges]
    return hashlib.sha256("\n".join(sorted(canonical)).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Repeated ISHA evaluation on labeled source-target snapshots.")
    parser.add_argument("--pairs", required=True, help="CSV with dataset,source,target columns.")
    parser.add_argument("--data-root", default=".", help="Base directory for relative source and target paths.")
    parser.add_argument("--alpha-values", default="0.1,0.4,0.7")
    parser.add_argument("--repeats", type=int, default=50)
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--seed-order", choices=("server", "sorted"), default="server")
    parser.add_argument("--seed-pool-manifest", help="Reuse an ordered seed-pool JSON from an earlier run.")
    parser.add_argument("--identity-ground-truth", action="store_true", required=True,
                        help="Explicitly confirm that shared node IDs define the benchmark ground truth.")
    parser.add_argument("--output-dir", required=True, help="A new directory; existing results are never overwritten.")
    args = parser.parse_args()
    alphas = [float(value) for value in args.alpha_values.split(",")]
    if not alphas or len(set(alphas)) != len(alphas) or any(not 0 < alpha <= 1 for alpha in alphas):
        parser.error("alpha-values must be distinct numbers in (0, 1].")
    if args.repeats < 2 or args.max_rounds < 1:
        parser.error("repeats must be at least 2, and max-rounds at least 1.")
    with Path(args.pairs).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"dataset", "source", "target"}.issubset(reader.fieldnames or []):
            parser.error("Pairs CSV must contain dataset,source,target columns.")
        pairs = list(reader)
    if not pairs:
        parser.error("No pairs were supplied.")
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    root = Path(args.data_root)
    frozen = json.loads(Path(args.seed_pool_manifest).read_text(encoding="utf-8")) if args.seed_pool_manifest else {}
    manifests, summaries, used_ids = {}, [], set()
    config = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                  alphas=alphas, repeats=args.repeats, max_rounds=args.max_rounds, seed_start=args.seed_start,
                  seed_order=args.seed_order, seed_pool_manifest=args.seed_pool_manifest,
                  ground_truth="All shared node IDs, including nodes covered by seed hyperedges.")
    (output / "run_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    with (output / "raw_results.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = None
        for pair in pairs:
            source_path, target_path = root / pair["source"], root / pair["target"]
            pair_id = source_path.stem + "_vs_" + target_path.stem
            if pair_id in used_ids:
                raise ValueError("Duplicate pair identifier; use distinct input filenames.")
            used_ids.add(pair_id)
            source, target = load_hypergraph(source_path), load_hypergraph(target_path)
            common = {frozenset(edge) for edge in source}.intersection({frozenset(edge) for edge in target})
            if not common:
                raise ValueError(f"{pair_id}: no identical hyperedges for benchmark seed sampling.")
            pool = [set(edge) for edge in common]
            if args.seed_pool_manifest:
                pool = [set(edge) for edge in frozen[pair_id]["ordered_pool"]]
                if len(pool) != len(common) or {frozenset(edge) for edge in pool} != common:
                    raise ValueError(f"{pair_id}: frozen seed pool does not match the input graphs.")
            elif args.seed_order == "sorted":
                pool.sort(key=lambda edge: tuple(sorted(edge)))
            nodes1, nodes2 = set().union(*source), set().union(*target)
            ground_truth = {node: node for node in nodes1 & nodes2}
            manifests[pair_id] = dict(
                source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                target_sha256=hashlib.sha256(target_path.read_bytes()).hexdigest(),
                ordered_pool=[sorted(edge) for edge in pool],
            )
            (output / "seed_pool_manifest.json").write_text(json.dumps(manifests, indent=2), encoding="utf-8")
            for alpha in alphas:
                rows = []
                for run in range(args.repeats):
                    run_seed = args.seed_start + run
                    sampled = random.Random(run_seed).sample(pool, max(1, int(alpha * len(pool))))
                    started = time.perf_counter()
                    matches = align_hypergraphs(source, target, [(edge, edge) for edge in sampled], args.max_rounds)
                    runtime = time.perf_counter() - started
                    row = dict(dataset=pair["dataset"], pair_id=pair_id, alpha=alpha, run_idx=run, run_seed=run_seed,
                               seed_count=len(sampled), seed_fingerprint=fingerprint(sampled), runtime_seconds=runtime,
                               **evaluate_alignment(matches, ground_truth))
                    if writer is None:
                        writer = csv.DictWriter(handle, fieldnames=list(row))
                        writer.writeheader()
                    writer.writerow(row)
                    handle.flush()
                    rows.append(row)
                summaries.append(dict(dataset=pair["dataset"], pair_id=pair_id, alpha=alpha, runs=args.repeats, **{
                    metric + "_" + name: function([row[metric] for row in rows])
                    for metric in ("precision", "recall", "f1")
                    for name, function in (("mean", statistics.mean), ("sample_sd", statistics.stdev))}))
                print(f"{pair_id}, alpha={alpha}: F1={summaries[-1]['f1_mean']:.3f} +/- {summaries[-1]['f1_sample_sd']:.3f}", flush=True)
    with (output / "summary.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)


if __name__ == "__main__":
    main()
