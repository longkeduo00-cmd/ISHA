from collections import defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np
import scipy.sparse as sp


def _select_matches(nodes, available_targets, evidence, degrees1, degrees2):
    candidates = []
    for source in nodes:
        start, end = evidence.indptr[source:source + 2]
        if start == end or degrees1.get(source, 0) == 0:
            continue
        for index in range(start, end):
            target = evidence.indices[index]
            if target not in available_targets or degrees2.get(target, 0) == 0:
                continue
            value = evidence.data[index]
            denominator = degrees1[source] + degrees2[target] - value
            # This is T/(K1+K2), with the server's validity guard and operation
            # order retained so floating-point ties are resolved identically.
            overlap = value / denominator if denominator > 0 else 0.0
            score = overlap / (1.0 + overlap)
            if score > 0:
                candidates.append((score, source, target))

    # Stable sorting preserves source-node and CSR-column order at equal scores.
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    best_source, best_target = {}, {}
    for score, source, target in candidates:
        if source not in best_source:
            best_source[source] = (target, score)
        if target not in best_target:
            best_target[target] = (source, score)
    return {
        source: (target, score)
        for source, (target, score) in best_source.items()
        if best_target[target][0] == source
    }


def _matched_overlap(source_edge, target_edge, matches):
    overlap = 0
    for source in source_edge:
        if source in matches and matches[source] in target_edge:
            overlap += 1
    return overlap


def iterative_hypergraph_alignment(
    g1_nodes: List[int],
    g2_nodes: Set[int],
    g1_hyperedges: List[Set[int]],
    g2_hyperedges: List[Set[int]],
    seed_pairs: List[Tuple[Set[int], Set[int]]],
    max_node_id: int,
    iterations: int = 10,
) -> Dict[int, int]:
    """Align nodes using seed hyperedges, mutual selection, and propagation."""
    evidence = sp.dok_matrix((max_node_id + 1, max_node_id + 1), dtype=np.float32)
    # Each aligned seed hyperedge contributes one to every internal node pair.
    for source_edge, target_edge in seed_pairs:
        for source in source_edge:
            for target in target_edge:
                evidence[source, target] += 1.0

    incident1, incident2 = defaultdict(list), defaultdict(list)
    degrees1, degrees2 = defaultdict(int), defaultdict(int)
    for edge in g1_hyperedges:
        for node in edge:
            incident1[node].append(edge)
            degrees1[node] += 1
    for edge in g2_hyperedges:
        for node in edge:
            incident2[node].append(edge)
            degrees2[node] += 1

    matches, matched_sources, matched_targets = {}, set(), set()
    for _ in range(iterations):
        nodes = [node for node in g1_nodes if node not in matched_sources]
        available_targets = g2_nodes - matched_targets
        if not nodes or not available_targets:
            break
        csr = evidence.tocsr()
        if csr.nnz == 0:
            break
        # Preserve the sorted CSR traversal previously triggered by the removed
        # normalization branch; this order determines equal-score selections.
        csr.sum_duplicates()
        accepted = _select_matches(nodes, available_targets, csr, degrees1, degrees2)
        if not accepted:
            break
        new_matches = {source: target for source, (target, _) in accepted.items()}
        matches.update(new_matches)
        matched_sources.update(new_matches)
        matched_targets.update(new_matches.values())

        updates = defaultdict(float)
        # Newly accepted matches support unmatched node pairs in incident edges.
        # Tied target edges prefer equal size, then smaller size, then more
        # unmatched targets; remaining ties retain the input edge order.
        for source, (target, match_score) in accepted.items():
            for source_edge in incident1[source]:
                best_edge, best_overlap = None, -1
                best_equal_size, best_size, best_unmatched = False, float("inf"), -1
                source_size = len(source_edge)
                for target_edge in incident2[target]:
                    overlap = _matched_overlap(source_edge, target_edge, matches)
                    size = len(target_edge)
                    equal_size = size == source_size
                    unmatched = len(target_edge.difference(matched_targets))
                    replace = overlap > best_overlap
                    if overlap == best_overlap and overlap > 0:
                        if best_equal_size:
                            replace = equal_size and unmatched > best_unmatched
                        else:
                            replace = equal_size or size < best_size or (size == best_size and unmatched > best_unmatched)
                    if replace:
                        best_edge, best_overlap = target_edge, overlap
                        best_equal_size, best_size, best_unmatched = equal_size, size, unmatched
                if best_edge is not None:
                    for node1 in source_edge:
                        if node1 in matched_sources:
                            continue
                        for node2 in best_edge:
                            if node2 not in matched_targets:
                                updates[(node1, node2)] += match_score
        evidence = evidence.todok()
        for (source, target), value in updates.items():
            evidence[source, target] += value

    return {int(source): int(target) for source, target in matches.items()}
