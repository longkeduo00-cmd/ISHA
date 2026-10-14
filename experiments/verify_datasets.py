import argparse
import csv
import hashlib
import json
from pathlib import Path

from isha.io import load_hypergraph


def verify(data_root="."):
    root = Path(data_root)
    manifest = json.loads((root / "datasets" / "manifest.json").read_text(encoding="utf-8"))
    expected_paths = set()
    with (root / "experiments" / "pairs_10_real.csv").open(encoding="utf-8-sig", newline="") as handle:
        pairs = list(csv.DictReader(handle))
    for pair in pairs:
        expected_paths.update((pair["source"], pair["target"]))
    if {entry["path"] for entry in manifest["files"]} != expected_paths:
        raise ValueError("Snapshot manifest and experiment pair list differ.")
    graphs = {}
    for entry in manifest["files"]:
        path = root / entry["path"]
        content = path.read_bytes()
        if len(content) != entry["bytes"] or hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Snapshot checksum mismatch: {entry['path']}")
        edges = load_hypergraph(path)
        nodes = set().union(*edges)
        if len(edges) != entry["hyperedges"] or len(nodes) != entry["nodes"]:
            raise ValueError(f"Snapshot statistics mismatch: {entry['path']}")
        graphs[entry["path"]] = edges
    seed_manifest = json.loads((root / "datasets" / "seed_pool_manifest.json").read_text(encoding="utf-8"))
    expected_pairs = set()
    for pair in pairs:
        pair_id = Path(pair["source"]).stem + "_vs_" + Path(pair["target"]).stem
        expected_pairs.add(pair_id)
        entry = seed_manifest[pair_id]
        source, target = root / pair["source"], root / pair["target"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry["source_sha256"]:
            raise ValueError(f"Seed-manifest source checksum mismatch: {pair_id}")
        if hashlib.sha256(target.read_bytes()).hexdigest() != entry["target_sha256"]:
            raise ValueError(f"Seed-manifest target checksum mismatch: {pair_id}")
        common = {frozenset(edge) for edge in graphs[pair["source"]]}.intersection(
            {frozenset(edge) for edge in graphs[pair["target"]]})
        pool = [frozenset(edge) for edge in entry["ordered_pool"]]
        if len(pool) != len(common) or set(pool) != common:
            raise ValueError(f"Frozen seed pool differs from the snapshots: {pair_id}")
    if set(seed_manifest) != expected_pairs:
        raise ValueError("Seed manifest and experiment pair list differ.")
    return {"verified_snapshots": len(graphs), "verified_pairs": len(pairs), "bytes": sum(entry["bytes"] for entry in manifest["files"])}


def main():
    parser = argparse.ArgumentParser(description="Verify the bundled paper dataset snapshots and frozen seed pools.")
    parser.add_argument("--data-root", default=".")
    args = parser.parse_args()
    print(json.dumps(verify(args.data_root), indent=2))


if __name__ == "__main__":
    main()
