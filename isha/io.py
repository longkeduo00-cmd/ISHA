import csv
from pathlib import Path


def load_hypergraph(path):
    edges = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            edge = set(map(int, line.split()))
            if min(edge) < 0:
                raise ValueError(f"{path}:{number}: node IDs must be nonnegative.")
            edges.append(edge)
    return edges


def load_seed_pairs(path, source_edges, target_edges):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"source_edge", "target_edge"}.issubset(reader.fieldnames or []):
            raise ValueError("Seed CSV must contain source_edge,target_edge columns.")
        pairs = []
        for row in reader:
            source, target = int(row["source_edge"]), int(row["target_edge"])
            if not 0 <= source < len(source_edges) or not 0 <= target < len(target_edges):
                raise ValueError("Seed edge indices must be valid zero-based positions.")
            pairs.append((source_edges[source], target_edges[target]))
    return pairs


def load_ground_truth(path):
    result = {}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"source", "target"}.issubset(reader.fieldnames or []):
            raise ValueError("Ground-truth CSV must contain source,target columns.")
        for row in reader:
            source, target = int(row["source"]), int(row["target"])
            if source in result:
                raise ValueError("Duplicate ground-truth source node.")
            result[source] = target
    return result


def save_matches(path, matches):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source", "target"])
        writer.writerows(sorted(matches.items()))
